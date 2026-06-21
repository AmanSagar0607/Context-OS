//! ContextOS SDK for Rust
//!
//! # Example
//! ```rust,no_run
//! use contextos::Client;
//!
//! #[tokio::main]
//! async fn main() -> Result<(), Box<dyn std::error::Error>> {
//!     let client = Client::new("https://api.contextos.dev", "your-api-key")?;
//!
//!     // Add memory
//!     let memory = client.memory().add("Important information").await?;
//!
//!     // Search
//!     let results = client.search().search("important information").await?;
//!
//!     Ok(())
//! }
//! ```

pub mod client;
pub mod error;
pub mod memory;
pub mod search;
pub mod crawl;
pub mod knowledge;

pub use client::Client;
pub use error::{Error, Result};
