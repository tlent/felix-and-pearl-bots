use flate2::read::GzDecoder;
use reqwest::header::{HeaderMap, ACCEPT, ACCEPT_ENCODING, ACCEPT_LANGUAGE, USER_AGENT};
use scraper::{Html, Selector};
use serenity::all::ChannelId;
use serenity::prelude::*;
use std::env;
use std::io::prelude::*;

const NATIONAL_DAYS_BASE_URL: &str = "https://www.nationaldaycalendar.com";
const NATIONAL_DAYS_READ_URL: &str = "https://www.nationaldaycalendar.com/read";

#[tokio::main]
async fn main() {
    let token = env::var("DISCORD_TOKEN").expect("Missing DISCORD_TOKEN environment variable");
    let intents = GatewayIntents::GUILD_MESSAGES | GatewayIntents::MESSAGE_CONTENT;
    let client = serenity::Client::builder(&token, intents)
        .await
        .expect("Error creating client");
    let mut headers = HeaderMap::new();
    headers.insert(
        ACCEPT,
        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            .parse()
            .unwrap(),
    );
    headers.insert(ACCEPT_ENCODING, "gzip, deflate, br".parse().unwrap());
    headers.insert(USER_AGENT, "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15".parse().unwrap());
    headers.insert(ACCEPT_LANGUAGE, "en-US,en;q=0.9".parse().unwrap());
    let gzip_bytes = reqwest::Client::new()
        .get(NATIONAL_DAYS_READ_URL)
        .headers(headers)
        .send()
        .await
        .expect("Error fetching national days page")
        .bytes()
        .await
        .expect("Error getting response text");
    let mut decoder = GzDecoder::new(&gzip_bytes[..]);
    let mut html = String::new();
    decoder
        .read_to_string(&mut html)
        .expect("Error decoding gzip html");
    let document = Html::parse_document(&html);
    let selector = Selector::parse(".m-card--header a").expect("Error parsing selector");
    let element = document
        .select(&selector)
        .next()
        .expect("Selector failed to find element");
    let read_more_url = element.attr("href").expect("Element missing href");
    let national_day_text = element.text().collect::<Vec<_>>().join("");
    let message =
        format!("{national_day_text}\n[Read more]({NATIONAL_DAYS_BASE_URL}{read_more_url})");
    if let Err(err) = ChannelId::new(1108866354980855961)
        .say(&client.http, message)
        .await
    {
        eprintln!("Error saying message: {err:?}");
    }
}
