use serde::{Deserialize, Serialize};

use crate::error::Result;

/// Crawl request.
#[derive(Debug, Serialize)]
pub struct CrawlRequest {
    pub url: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub depth: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_pages: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub extract: Option<bool>,
}

/// Crawl result.
#[derive(Debug, Deserialize)]
pub struct CrawlResult {
    pub id: String,
    pub url: String,
    pub title: String,
    pub content: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub links: Option<Vec<String>>,
}

/// Crawl response.
#[derive(Debug, Deserialize)]
pub struct CrawlResponse {
    pub result: CrawlResult,
    pub status: String,
}

/// Crawl service.
pub struct CrawlService {
    base_url: String,
    api_key: String,
}

impl CrawlService {
    pub(crate) fn new(base_url: String, api_key: String) -> Self {
        CrawlService { base_url, api_key }
    }

    /// Crawl a URL.
    pub async fn crawl(&self, url: &str) -> Result<CrawlResponse> {
        let req = CrawlRequest {
            url: url.to_string(),
            depth: None,
            max_pages: None,
            extract: None,
        };

        let url = format!("{}/api/v1/crawl", self.base_url);
        let resp = reqwest::Client::new()
            .post(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .json(&req)
            .send()
            .await
            .map_err(|e| crate::error::Error::Request(e.to_string()))?;

        let result: CrawlResponse = resp
            .json()
            .await
            .map_err(|e| crate::error::Error::Serialization(e.to_string()))?;

        Ok(result)
    }

    /// Extract content from a URL.
    pub async fn extract(&self, url: &str) -> Result<CrawlResponse> {
        let req = CrawlRequest {
            url: url.to_string(),
            depth: None,
            max_pages: None,
            extract: Some(true),
        };

        let url = format!("{}/api/v1/crawl", self.base_url);
        let resp = reqwest::Client::new()
            .post(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .json(&req)
            .send()
            .await
            .map_err(|e| crate::error::Error::Request(e.to_string()))?;

        let result: CrawlResponse = resp
            .json()
            .await
            .map_err(|e| crate::error::Error::Serialization(e.to_string()))?;

        Ok(result)
    }
}
