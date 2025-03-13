use chrono::NaiveDate;

/// Represents a national day with its name and URL path
#[derive(Debug)]
pub struct NationalDay {
    /// The name of the national day
    pub name: String,
    /// The URL path (without base URL) to the national day's page
    pub url: String,
}

/// Contains all data needed for generating the daily message
#[derive(Debug)]
pub struct DailyData {
    /// Today's date
    pub date: NaiveDate,
    /// List of national days for today
    pub national_days: Vec<NationalDay>,
    /// Optional birthday message if someone has a birthday today
    pub birthday: Option<String>,
} 