use anyhow::{Context, Result};
use log::debug;
use rusqlite::OptionalExtension;

use crate::models::{DailyData, NationalDay};

/// Fetches all data needed for today's message from the database
///
/// # Arguments
/// * `db_connection` - SQLite database connection
/// * `date_str` - Today's date formatted as YYYY-MM-DD
/// * `formatted_date` - Today's date formatted for display (e.g., "Monday, January 1, 2025")
///
/// # Returns
/// A `DailyData` struct containing today's date, national days, and any birthdays
pub fn fetch_daily_data(
    db_connection: &rusqlite::Connection,
    date_str: &str,
    formatted_date: &str,
) -> Result<DailyData> {
    let national_days = get_national_days(db_connection, date_str)?;
    let birthday = get_birthday(db_connection, date_str)?;
    
    Ok(DailyData {
        date_str: date_str.to_string(),
        formatted_date: formatted_date.to_string(),
        national_days,
        birthday,
    })
}

/// Retrieves national days for the given date from the database
///
/// # Arguments
/// * `db_connection` - SQLite database connection
/// * `date_str` - Date formatted as YYYY-MM-DD
///
/// # Returns
/// A vector of `NationalDay` structs
fn get_national_days(
    db_connection: &rusqlite::Connection,
    date_str: &str,
) -> Result<Vec<NationalDay>> {
    let mut statement = db_connection
        .prepare("SELECT name, url FROM NationalDay WHERE occurrence_2025 = ?1")
        .context("Failed to prepare national days query")?;
    
    let rows = statement
        .query_map([date_str], |row| {
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
/// * `date_str` - Date formatted as YYYY-MM-DD
///
/// # Returns
/// An optional string containing birthday information, or None if no birthdays today
fn get_birthday(
    db_connection: &rusqlite::Connection,
    date_str: &str,
) -> Result<Option<String>> {
    let result = db_connection
        .query_row(
            "SELECT description FROM Birthday WHERE date = ?1",
            [date_str],
            |row| row.get(0),
        )
        .optional()
        .context("Failed to query birthday")?;
    
    if result.is_some() {
        debug!("Found birthday for today");
    }
    
    Ok(result)
} 