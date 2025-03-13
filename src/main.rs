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

use chrono::Local;
use log::info;
use std::env;
use anyhow::{Context, Result};

use felix_bot::config::{DB_PATH, NATIONAL_DAY_BASE_URL};
use felix_bot::database;
use felix_bot::ai;
use felix_bot::discord;

/// Main entry point for the Felix Bot application
///
/// Initializes logging, loads environment variables, connects to the database,
/// fetches daily data, generates a message using Claude AI, and sends it to Discord.
fn main() -> Result<()> {
    // Initialize logging
    simple_logger::SimpleLogger::new().init().context("Failed to initialize logger")?;
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
        .with_context(|| format!("Failed to open database at {}", DB_PATH))?;
    
    // Get today's date
    let today = Local::now().naive_local().date();
    let ymd_date = today.format("%Y-%m-%d").to_string();
    
    // Fetch daily data
    let daily_data = database::fetch_daily_data(&db_connection, today, &ymd_date)?;
    
    // Generate message using LLM
    let llm_message = ai::generate_llm_message(&anthropic_api_key, &daily_data)?;
    
    // Build and send message
    let message = discord::build_message(&daily_data, &llm_message, NATIONAL_DAY_BASE_URL)?;
    
    if test_mode {
        info!("Test mode: Message generated successfully but not sent");
        info!("Message preview (first 100 chars): {}", &message.chars().take(100).collect::<String>());
    } else {
        discord::send_message(&discord_token, &message)?;
        info!("Message sent successfully");
    }
    
    Ok(())
}
