use anyhow::{anyhow, Context, Result};
use rusqlite::OptionalExtension;
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::{env, fs, path::Path};
use time::macros::format_description;
use time::{Date, OffsetDateTime};
use tracing::{debug, error, info, instrument};

// Configuration constants
#[derive(Debug, Deserialize, Serialize)]
struct Config {
    national_day_base_url: String,
    discord_api_url: String,
    db_path: String,
    channel_id: u64,
    discord_max_message_len: usize,
    anthropic_api_url: String,
    claude_model: String,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            national_day_base_url: "https://www.nationaldaycalendar.com".to_string(),
            discord_api_url: "https://discord.com/api/v10".to_string(),
            db_path: "days.db".to_string(),
            channel_id: 1218191951237742612,
            discord_max_message_len: 2000,
            anthropic_api_url: "https://api.anthropic.com/v1/messages".to_string(),
            claude_model: "claude-3-5-haiku-latest".to_string(),
        }
    }
}

// Models
#[derive(Debug)]
struct NationalDay {
    name: String,
    url: String,
}

#[derive(Debug)]
struct DailyData {
    date: Date,
    national_days: Vec<NationalDay>,
    birthday: Option<String>,
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize logging
    tracing_subscriber::fmt::init();
    info!("Starting Felix Bot");

    // Load configuration
    let config = load_config().context("Failed to load configuration")?;
    debug!(?config, "Configuration loaded");

    // Load environment variables
    let anthropic_api_key = env::var("ANTHROPIC_API_KEY")
        .context("ANTHROPIC_API_KEY environment variable not set")?;
    let discord_token = env::var("DISCORD_TOKEN")
        .context("DISCORD_TOKEN environment variable not set")?;

    // Initialize database connection
    let db_connection = rusqlite::Connection::open(&config.db_path)
        .context(format!("Failed to open database at {}", &config.db_path))?;
    
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
        &config,
        &daily_data,
    )
    .await
    .context("Failed to generate LLM message")?;
    
    // Build and send message
    let message = build_message(&config, &daily_data, &llm_message)?;
    
    send_message(&http_client, &discord_token, &config, &message).await
        .context("Failed to send Discord message")?;
    
    info!("Message sent successfully");
    Ok(())
}

fn load_config() -> Result<Config> {
    let config_path = "config.json";
    
    if Path::new(config_path).exists() {
        let config_str = fs::read_to_string(config_path)
            .context("Failed to read config file")?;
        let config: Config = serde_json::from_str(&config_str)
            .context("Failed to parse config file")?;
        Ok(config)
    } else {
        let config = Config::default();
        let config_str = serde_json::to_string_pretty(&config)
            .context("Failed to serialize default config")?;
        fs::write(config_path, config_str)
            .context("Failed to write default config file")?;
        info!("Created default configuration file at {}", config_path);
        Ok(config)
    }
}

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

#[instrument(skip(http_client, api_key, config))]
async fn generate_llm_message(
    http_client: &reqwest::Client,
    api_key: &str,
    config: &Config,
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
            "model": config.claude_model,
            "messages": [
                { "role": "user", "content": prompt }
            ],
            "max_tokens": 1000
        }
    );
    
    debug!("Sending request to Anthropic API");
    let response = http_client
        .post(&config.anthropic_api_url)
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

#[instrument(skip(config, daily_data, llm_message))]
fn build_message(
    config: &Config,
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
            config.national_day_base_url, 
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

#[instrument(skip(client, discord_token, config, message))]
async fn send_message(
    client: &reqwest::Client,
    discord_token: &str,
    config: &Config,
    message: &str,
) -> Result<()> {
    if message.len() <= config.discord_max_message_len {
        send_discord_message(client, discord_token, config, message).await
    } else {
        send_multipart_discord_message(client, discord_token, config, message).await
    }
}

#[instrument(skip(client, discord_token, config, message))]
async fn send_multipart_discord_message(
    client: &reqwest::Client,
    discord_token: &str,
    config: &Config,
    message: &str,
) -> Result<()> {
    let mut current_message = String::new();
    let paragraphs = message.split_inclusive("\n\n");
    
    for paragraph in paragraphs {
        if current_message.len() + paragraph.len() > config.discord_max_message_len {
            send_discord_message(client, discord_token, config, &current_message).await?;
            current_message.clear();
            debug!("Sent partial message");
        }
        current_message.push_str(paragraph);
    }
    
    if !current_message.is_empty() {
        send_discord_message(client, discord_token, config, &current_message).await?;
        debug!("Sent final part of multipart message");
    }
    
    Ok(())
}

#[instrument(skip(client, discord_token, config, message))]
async fn send_discord_message(
    client: &reqwest::Client,
    discord_token: &str,
    config: &Config,
    message: &str,
) -> Result<()> {
    let url = format!("{}/channels/{}/messages", 
        config.discord_api_url, 
        config.channel_id
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
