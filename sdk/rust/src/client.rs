use reqwest::Client as ReqwestClient;
use serde::{Deserialize, Serialize};

use crate::error::{Error, Result};
use crate::memory::MemoryService;
use crate::search::SearchService;
use crate::crawl::CrawlService;
use crate::knowledge::KnowledgeService;

const DEFAULT_BASE_URL: &str = "https://api.contextos.dev";

/// ContextOS API client.
pub struct Client {
    base_url: String,
    api_key: String,
    http_client: ReqwestClient,
    memory: MemoryService,
    search: SearchService,
    crawl: CrawlService,
    knowledge: KnowledgeService,
}

impl Client {
    /// Create a new ContextOS client.
    pub fn new(base_url: &str, api_key: &str) -> Result<Self> {
        let base_url = if base_url.is_empty() {
            DEFAULT_BASE_URL.to_string()
        } else {
            base_url.to_string()
        };

        let http_client = ReqwestClient::builder()
            .timeout(std::time::Duration::from_secs(30))
            .build()
            .map_err(|e| Error::Client(e.to_string()))?;

        let client = Client {
            base_url,
            api_key: api_key.to_string(),
            http_client,
            memory: MemoryService::new(base_url.clone(), api_key.to_string()),
            search: SearchService::new(base_url.clone(), api_key.to_string()),
            crawl: CrawlService::new(base_url.clone(), api_key.to_string()),
            knowledge: KnowledgeService::new(base_url.clone(), api_key.to_string()),
        };

        Ok(client)
    }

    /// Get memory service.
    pub fn memory(&self) -> &MemoryService {
        &self.memory
    }

    /// Get search service.
    pub fn search(&self) -> &SearchService {
        &self.search
    }

    /// Get crawl service.
    pub fn crawl(&self) -> &CrawlService {
        &self.crawl
    }

    /// Get knowledge service.
    pub fn knowledge(&self) -> &KnowledgeService {
        &self.knowledge
    }

    /// Perform a GET request.
    pub async fn get(&self, path: &str) -> Result<reqwest::Response> {
        let url = format!("{}{}", self.base_url, path);
        let resp = self.http_client
            .get(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .send()
            .await
            .map_err(|e| Error::Request(e.to_string()))?;

        if resp.status().is_success() {
            Ok(resp)
        } else {
            let status = resp.status().as_u16();
            let text = resp.text().await.unwrap_or_default();
            Err(Error::Api { status, message: text })
        }
    }

    /// Perform a POST request.
    pub async fn post<T: Serialize>(&self, path: &str, body: &T) -> Result<reqwest::Response> {
        let url = format!("{}{}", self.base_url, path);
        let resp = self.http_client
            .post(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .json(body)
            .send()
            .await
            .map_err(|e| Error::Request(e.to_string()))?;

        if resp.status().is_success() {
            Ok(resp)
        } else {
            let status = resp.status().as_u16();
            let text = resp.text().await.unwrap_or_default();
            Err(Error::Api { status, message: text })
        }
    }

    /// Perform a PUT request.
    pub async fn put<T: Serialize>(&self, path: &str, body: &T) -> Result<reqwest::Response> {
        let url = format!("{}{}", self.base_url, path);
        let resp = self.http_client
            .put(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .json(body)
            .send()
            .await
            .map_err(|e| Error::Request(e.to_string()))?;

        if resp.status().is_success() {
            Ok(resp)
        } else {
            let status = resp.status().as_u16();
            let text = resp.text().await.unwrap_or_default();
            Err(Error::Api { status, message: text })
        }
    }

    /// Perform a DELETE request.
    pub async fn delete(&self, path: &str) -> Result<reqwest::Response> {
        let url = format!("{}{}", self.base_url, path);
        let resp = self.http_client
            .delete(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .send()
            .await
            .map_err(|e| Error::Request(e.to_string()))?;

        if resp.status().is_success() {
            Ok(resp)
        } else {
            let status = resp.status().as_u16();
            let text = resp.text().await.unwrap_or_default();
            Err(Error::Api { status, message: text })
        }
    }
}
