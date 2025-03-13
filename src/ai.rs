use anyhow::{Context, Result};
use log::debug;
use serde_json::json;

use crate::models::DailyData;
use crate::config::ANTHROPIC_API_URL;
use crate::config::CLAUDE_MODEL;

/// Generates a creative message using Claude AI based on today's national days and special occasions
///
/// # Arguments
/// * `api_key` - Anthropic API key
/// * `daily_data` - Data about today's date, national days, and birthdays
///
/// # Returns
/// A string containing the AI-generated message
pub fn generate_llm_message(
    api_key: &str,
    daily_data: &DailyData,
) -> Result<String> {
    // Use the pre-formatted date string
    let formatted_date = &daily_data.formatted_date;
    
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
    
    let response = ureq::post(ANTHROPIC_API_URL)
        .set("Content-Type", "application/json")
        .set("x-api-key", api_key)
        .set("anthropic-version", "2023-06-01")
        .send_json(&request_body)
        .context("Failed to send request to Anthropic API")?;
    
    let response_body: serde_json::Value = response.into_json()
        .context("Failed to parse Anthropic API response")?;
    
    let llm_message = response_body["content"][0]["text"]
        .as_str()
        .ok_or_else(|| anyhow::anyhow!("Failed to extract message from Anthropic API response"))?
        .to_owned();
    
    debug!("Successfully generated LLM message");
    Ok(llm_message)
} 