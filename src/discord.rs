use anyhow::{Context, Result};
use log::{debug, error};
use serde_json::json;

use crate::config::{DISCORD_API_URL, DISCORD_MAX_MESSAGE_LEN, CHANNEL_ID};
use crate::models::DailyData;

/// Builds the complete message to be sent to Discord
///
/// # Arguments
/// * `daily_data` - Data about today's date, national days, and birthdays
/// * `llm_message` - The AI-generated message from Claude
/// * `national_day_base_url` - Base URL for national day links
///
/// # Returns
/// A formatted string containing the complete message with date, national days, birthdays, and AI content
pub fn build_message(
    daily_data: &DailyData,
    llm_message: &str,
    national_day_base_url: &str,
) -> Result<String> {
    let mut message = daily_data.date.format("%A, %B %e, %Y").to_string();
    
    // Add national days
    for day in &daily_data.national_days {
        message.push_str(&format!(" | [{}]({}{})", 
            day.name, 
            national_day_base_url, 
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
/// * `discord_token` - Discord bot token
/// * `message` - The message to send
///
/// # Returns
/// Result indicating success or failure
pub fn send_message(
    discord_token: &str,
    message: &str,
) -> Result<()> {
    if message.len() <= DISCORD_MAX_MESSAGE_LEN {
        send_discord_message(discord_token, message)
    } else {
        send_multipart_discord_message(discord_token, message)
    }
}

/// Splits a long message into multiple parts and sends each part to Discord
///
/// # Arguments
/// * `discord_token` - Discord bot token
/// * `message` - The long message to split and send
///
/// # Returns
/// Result indicating success or failure
fn send_multipart_discord_message(
    discord_token: &str,
    message: &str,
) -> Result<()> {
    let mut current_message = String::new();
    let paragraphs = message.split_inclusive("\n\n");
    
    for paragraph in paragraphs {
        if current_message.len() + paragraph.len() > DISCORD_MAX_MESSAGE_LEN {
            send_discord_message(discord_token, &current_message)?;
            current_message.clear();
            debug!("Sent partial message");
        }
        current_message.push_str(paragraph);
    }
    
    if !current_message.is_empty() {
        send_discord_message(discord_token, &current_message)?;
        debug!("Sent final part of multipart message");
    }
    
    Ok(())
}

/// Sends a single message to a Discord channel
///
/// # Arguments
/// * `discord_token` - Discord bot token
/// * `message` - The message to send
///
/// # Returns
/// Result indicating success or failure
fn send_discord_message(
    discord_token: &str,
    message: &str,
) -> Result<()> {
    let url = format!("{}/channels/{}/messages", 
        DISCORD_API_URL, 
        CHANNEL_ID
    );
    
    let response = ureq::post(&url)
        .set("Authorization", &format!("Bot {discord_token}"))
        .set("Content-Type", "application/json")
        .send_json(json!({ "content": message }))
        .context("Failed to send Discord message request")?;
    
    if response.status() < 200 || response.status() >= 300 {
        let error_text = response.into_string()
            .context("Failed to get Discord error response")?;
        error!("Discord API error: {}", error_text);
        return Err(anyhow::anyhow!("Discord API error: {}", error_text));
    }
    
    Ok(())
} 