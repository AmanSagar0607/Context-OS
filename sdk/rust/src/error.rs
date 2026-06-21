use thiserror::Error;

/// ContextOS error type.
#[derive(Error, Debug)]
pub enum Error {
    #[error("API error {status}: {message}")]
    Api { status: u16, message: String },

    #[error("Client error: {0}")]
    Client(String),

    #[error("Request error: {0}")]
    Request(String),

    #[error("Serialization error: {0}")]
    Serialization(String),

    #[error("Not found: {0}")]
    NotFound(String),

    #[error("Unauthorized: {0}")]
    Unauthorized(String),

    #[error("Rate limited")]
    RateLimited,

    #[error("Server error: {0}")]
    Server(String),
}

/// ContextOS result type.
pub type Result<T> = std::result::Result<T, Error>;
