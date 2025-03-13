//! Felix Bot - A Discord bot that posts daily messages about national days and special occasions
//! 
//! This bot fetches national days and birthdays from a SQLite database, generates creative messages
//! using Claude AI, and posts them to a Discord channel. The messages are written from the perspective
//! of a cat named Sir Felix Whiskersworth.
//!
//! # Environment Variables
//! - `ANTHROPIC_API_KEY`: API key for Anthropic's Claude AI
//! - `DISCORD_TOKEN`: Discord bot token
//!
//! # Command Line Arguments
//! - `--test-mode`: Run in test mode to verify functionality without sending messages

use anyhow::{anyhow, Context, Result};
use rusqlite::OptionalExtension;
use serde_json::json;
use std::env;
use time::macros::format_description;
use time::{Date, OffsetDateTime};
use tracing::{debug, error, info, instrument};

// Configuration constants
const NATIONAL_DAY_BASE_URL: &str = "https://www.nationaldaycalendar.com";
const DISCORD_API_URL: &str = "https://discord.com/api/v10";
const DB_PATH: &str = "days.db";
const CHANNEL_ID: u64 = 1218191951237742612;
const DISCORD_MAX_MESSAGE_LEN: usize = 2000;
const ANTHROPIC_API_URL: &str = "https://api.anthropic.com/v1/messages";
const CLAUDE_MODEL: &str = "claude-3-5-haiku-latest";

/// Represents a national day with its name and URL path
#[derive(Debug)]
struct NationalDay {
    /// The name of the national day
    name: String,
    /// The URL path (without base URL) to the national day's page
    url: String,
}

/// Contains all data needed for generating the daily message
#[derive(Debug)]
struct DailyData {
    /// Today's date
    date: Date,
    /// List of national days for today
    national_days: Vec<NationalDay>,
    /// Optional birthday message if someone has a birthday today
    birthday: Option<String>,
}

/// Main entry point for the Felix Bot application
///
/// Initializes logging, loads environment variables, connects to the database,
/// fetches daily data, generates a message using Claude AI, and sends it to Discord.
#[tokio::main]
async fn main() -> Result<()> {
    // Initialize logging
    tracing_subscriber::fmt::init();
    info!("Starting Felix Bot");

    // Check for test mode
    let args: Vec<String> = env::args().collect();
    let test_mode = args.iter().any(|arg| arg == "--test-mode");
    
    if test_mode {
        info!("Running in test mode - will verify functionality without sending messages");
    }

    // Load environment variables
    let anthropic_api_key = env::var("ANTHROPIC_API_KEY")
        .context("ANTHROPIC_API_KEY environment variable not set")?;
    let discord_token = env::var("DISCORD_TOKEN")
        .context("DISCORD_TOKEN environment variable not set")?;

    // Initialize database connection
    let db_connection = rusqlite::Connection::open(DB_PATH)
        .context(format!("Failed to open database at {}", DB_PATH))?;
    
    // Initialize HTTP client
    let http_client = reqwest::Client::new();
    
    // Get today's date
    let date = OffsetDateTime::now_utc().date();
    let ymd_date = date.format(format_description!("[year]-[month]-[day]"))?;
    
    // Fetch daily data
    let daily_data = fetch_daily_data(&db_connection, date, &ymd_date)
        .context("Failed to fetch daily data")?;
    
    // Generate message using LLM
    let llm_message = generate_llm_message(
        &http_client,
        &anthropic_api_key,
        &daily_data,
    )
    .await
    .context("Failed to generate LLM message")?;
    
    // Build and send message
    let message = build_message(&daily_data, &llm_message)?;
    
    if test_mode {
        info!("Test mode: Message generated successfully but not sent");
        info!("Message preview (first 100 chars): {}", &message.chars().take(100).collect::<String>());
    } else {
        send_message(&http_client, &discord_token, &message).await
            .context("Failed to send Discord message")?;
        info!("Message sent successfully");
    }
    
    Ok(())
}

/// Fetches all data needed for today's message from the database
///
/// # Arguments
/// * `db_connection` - SQLite database connection
/// * `date` - Today's date
/// * `ymd_date` - Today's date formatted as YYYY-MM-DD
///
/// # Returns
/// A `DailyData` struct containing today's date, national days, and any birthdays
#[instrument(skip(db_connection))]
fn fetch_daily_data(
    db_connection: &rusqlite::Connection,
    date: Date,
    ymd_date: &str,
) -> Result<DailyData> {
    let national_days = get_national_days(db_connection, ymd_date)
        .context("Failed to get national days")?;
    let birthday = get_birthday(db_connection, ymd_date)
        .context("Failed to get birthday")?;
    
    Ok(DailyData {
        date,
        national_days,
        birthday,
    })
}

/// Retrieves national days for the given date from the database
///
/// # Arguments
/// * `db_connection` - SQLite database connection
/// * `ymd_date` - Date formatted as YYYY-MM-DD
///
/// # Returns
/// A vector of `NationalDay` structs
#[instrument(skip(db_connection))]
fn get_national_days(
    db_connection: &rusqlite::Connection,
    ymd_date: &str,
) -> Result<Vec<NationalDay>> {
    let mut statement = db_connection
        .prepare("SELECT name, url FROM NationalDay WHERE occurrence_2025 = ?1")
        .context("Failed to prepare national days query")?;
    
    let rows = statement
        .query_map([&ymd_date], |row| {
            Ok(NationalDay {
                name: row.get(0)?,
                url: row.get(1)?,
            })
        })
        .context("Failed to execute national days query")?;
    
    let mut days = Vec::new();
    for day in rows {
        days.push(day.context("Failed to process national day row")?);
    }
    
    debug!("Found {} national days", days.len());
    Ok(days)
}

/// Retrieves birthday information for the given date from the database
///
/// # Arguments
/// * `db_connection` - SQLite database connection
/// * `ymd_date` - Date formatted as YYYY-MM-DD
///
/// # Returns
/// An optional string containing birthday information, or None if no birthdays today
#[instrument(skip(db_connection))]
fn get_birthday(
    db_connection: &rusqlite::Connection,
    ymd_date: &str,
) -> Result<Option<String>> {
    let result = db_connection
        .query_row(
            "SELECT description FROM Birthday WHERE date = ?1",
            [&ymd_date],
            |row| row.get(0),
        )
        .optional()
        .context("Failed to query birthday")?;
    
    if result.is_some() {
        debug!("Found birthday for today");
    }
    
    Ok(result)
}

/// Generates a creative message using Claude AI based on today's national days and special occasions
///
/// # Arguments
/// * `http_client` - HTTP client for making API requests
/// * `api_key` - Anthropic API key
/// * `daily_data` - Data about today's date, national days, and birthdays
///
/// # Returns
/// A string containing the AI-generated message
#[instrument(skip(http_client, api_key))]
async fn generate_llm_message(
    http_client: &reqwest::Client,
    api_key: &str,
    daily_data: &DailyData,
) -> Result<String> {
    let formatted_date = daily_data.date.format(format_description!(
        "[weekday], [month repr:long] [day padding:none], [year]"
    ))?;
    
    let formatted_national_days = daily_data.national_days
        .iter()
        .map(|day| day.name.as_str())
        .collect::<Vec<_>>()
        .join("\n");
    
    let birthday_line = daily_data.birthday
        .as_deref()
        .unwrap_or("None")
        .to_string();
    
    let prompt = format!(
        "Today's date is {formatted_date}. Below are today's national days and any special occasions to inspire your message:  
**National Days:** {formatted_national_days}  
**Special Occasions:** {birthday_line}  

You are Sir Felix Whiskersworth, our family's distinguished black-and-white feline, once simply Felix, now knighted for your charm and wisdom. Your task is to craft a daily message that transforms today's national days and any special occasions (like birthdays) into a single, captivating tale or reflection, as seen through your sharp, cat-like eyes.  

Here's how to make it purrfect:  
- **Weave a Seamless Story:** Blend all the national days and special occasions into one cohesive narrative or witty commentary. Avoid a mere list—let each element flow naturally into the next, as if you're stalking a thread of yarn through the day.  
- **Feline Perspective:** Reflect on these human holidays and events with a cat's curiosity, humor, or indifference. How might they connect to your world of napping, hunting, or preening? Make it uniquely yours.  
- **Tone:** Strike a balance between elegance (befitting your noble title) and playfulness (true to your whiskered spirit). Be witty, charming, and a tad mischievous, but never stiff or silly.  
- **Structure:** Begin with a feline observation about the day—perhaps the weather, a sunbeam, or a human's antics. Then, deftly tie in the national days and special occasions, letting your thoughts pounce from one to the next. Conclude with a clever, cat-inspired quip or a gracious farewell.  
- **Emojis:** Sprinkle in 3–5 relevant, humorous emojis to amplify your personality (e.g., 🐾 for paw prints, 😸 for feline glee). No hashtags allowed—this isn't a social media chase!  

End your message with a dashing sign-off, such as \"Yours in whiskers and wisdom, Sir Felix Whiskersworth,\" tailored to the day's mood. Keep it concise yet rich—think of it as a purrfectly groomed coat: sleek, shiny, and full of character. Now, unleash your feline brilliance!"
    );
    
    let request_body = json!(
        {
            "model": CLAUDE_MODEL,
            "messages": [
                { "role": "user", "content": prompt }
            ],
            "max_tokens": 1000
        }
    );
    
    debug!("Sending request to Anthropic API");
    let response = http_client
        .post(ANTHROPIC_API_URL)
        .header(reqwest::header::CONTENT_TYPE, "application/json")
        .header("x-api-key", api_key)
        .header("anthropic-version", "2023-06-01")
        .json(&request_body)
        .send()
        .await
        .context("Failed to send request to Anthropic API")?;
        
    if !response.status().is_success() {
        let error_text = response.text().await
            .context("Failed to get error response text")?;
        error!("Anthropic API error: {}", error_text);
        return Err(anyhow!("Anthropic API error: {}", error_text));
    }
    
    let response_body = response.text().await
        .context("Failed to get response body")?;
    
    let json: serde_json::Value = serde_json::from_str(&response_body)
        .context("Failed to parse Anthropic API response")?;
    
    let llm_message = json["content"][0]["text"]
        .as_str()
        .ok_or_else(|| anyhow!("Failed to extract message from Anthropic API response"))?
        .to_owned();
    
    debug!("Successfully generated LLM message");
    Ok(llm_message)
}

/// Builds the complete message to be sent to Discord
///
/// # Arguments
/// * `daily_data` - Data about today's date, national days, and birthdays
/// * `llm_message` - The AI-generated message from Claude
///
/// # Returns
/// A formatted string containing the complete message with date, national days, birthdays, and AI content
#[instrument(skip(daily_data, llm_message))]
fn build_message(
    daily_data: &DailyData,
    llm_message: &str,
) -> Result<String> {
    let mut message = daily_data.date.format(format_description!(
        "[weekday], [month repr:long] [day padding:none], [year]"
    ))?;
    
    // Add national days
    for day in &daily_data.national_days {
        message.push_str(&format!(" | [{}]({}{})", 
            day.name, 
            NATIONAL_DAY_BASE_URL, 
            day.url
        ));
    }
    
    // Add birthday if present
    if let Some(birthday) = &daily_data.birthday {
        message.push_str(&format!(" | {}", birthday));
    }
    
    // Add LLM message
    message.push('\n');
    message.push_str(llm_message);
    
    Ok(message)
}

/// Sends a message to Discord, handling messages that exceed Discord's character limit
///
/// # Arguments
/// * `client` - HTTP client for making API requests
/// * `discord_token` - Discord bot token
/// * `message` - The message to send
///
/// # Returns
/// Result indicating success or failure
#[instrument(skip(client, discord_token, message))]
async fn send_message(
    client: &reqwest::Client,
    discord_token: &str,
    message: &str,
) -> Result<()> {
    if message.len() <= DISCORD_MAX_MESSAGE_LEN {
        send_discord_message(client, discord_token, message).await
    } else {
        send_multipart_discord_message(client, discord_token, message).await
    }
}

/// Splits a long message into multiple parts and sends each part to Discord
///
/// # Arguments
/// * `client` - HTTP client for making API requests
/// * `discord_token` - Discord bot token
/// * `message` - The long message to split and send
///
/// # Returns
/// Result indicating success or failure
#[instrument(skip(client, discord_token, message))]
async fn send_multipart_discord_message(
    client: &reqwest::Client,
    discord_token: &str,
    message: &str,
) -> Result<()> {
    let mut current_message = String::new();
    let paragraphs = message.split_inclusive("\n\n");
    
    for paragraph in paragraphs {
        if current_message.len() + paragraph.len() > DISCORD_MAX_MESSAGE_LEN {
            send_discord_message(client, discord_token, &current_message).await?;
            current_message.clear();
            debug!("Sent partial message");
        }
        current_message.push_str(paragraph);
    }
    
    if !current_message.is_empty() {
        send_discord_message(client, discord_token, &current_message).await?;
        debug!("Sent final part of multipart message");
    }
    
    Ok(())
}

/// Sends a single message to a Discord channel
///
/// # Arguments
/// * `client` - HTTP client for making API requests
/// * `discord_token` - Discord bot token
/// * `message` - The message to send
///
/// # Returns
/// Result indicating success or failure
#[instrument(skip(client, discord_token, message))]
async fn send_discord_message(
    client: &reqwest::Client,
    discord_token: &str,
    message: &str,
) -> Result<()> {
    let url = format!("{}/channels/{}/messages", 
        DISCORD_API_URL, 
        CHANNEL_ID
    );
    
    let response = client
        .post(&url)
        .header(
            reqwest::header::AUTHORIZATION,
            format!("Bot {discord_token}"),
        )
        .header(reqwest::header::CONTENT_TYPE, "application/json")
        .json(&json!({ "content": message }))
        .send()
        .await
        .context("Failed to send Discord message request")?;
    
    if !response.status().is_success() {
        let error_text = response.text().await
            .context("Failed to get Discord error response")?;
        error!("Discord API error: {}", error_text);
        return Err(anyhow!("Discord API error: {}", error_text));
    }
    
    Ok(())
}
