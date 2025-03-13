//! Felix Bot - A Discord bot that posts daily messages about national days and special occasions
//! 
//! This bot fetches national days and birthdays from a SQLite database, generates creative messages
//! using Claude AI, and posts them to a Discord channel. The messages are written from the perspective
//! of a cat named Sir Felix Whiskersworth.

pub mod models;
pub mod database;
pub mod ai;
pub mod discord;
pub mod config; 