use serde::{Deserialize, Serialize};

use crate::error::Result;

/// Search request.
#[derive(Debug, Serialize)]
pub struct SearchRequest {
    pub query: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub top_k: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub threshold: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub mode: Option<String>,
}

/// Search hit.
#[derive(Debug, Deserialize)]
pub struct SearchHit {
    pub id: String,
    pub content: String,
    pub score: f64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub metadata: Option<std::collections::HashMap<String, String>>,
}

/// Search response.
#[derive(Debug, Deserialize)]
pub struct SearchResponse {
    pub hits: Vec<SearchHit>,
    pub query: String,
    pub total_hits: u32,
}

/// Search service.
pub struct SearchService {
    base_url: String,
    api_key: String,
}

impl SearchService {
    pub(crate) fn new(base_url: String, api_key: String) -> Self {
        SearchService { base_url, api_key }
    }

    /// Perform a hybrid search.
    pub async fn search(&self, query: &str, top_k: Option<u32>) -> Result<SearchResponse> {
        let req = SearchRequest {
            query: query.to_string(),
            top_k,
            threshold: None,
            mode: None,
        };

        let url = format!("{}/api/v1/search", self.base_url);
        let resp = reqwest::Client::new()
            .post(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .json(&req)
            .send()
            .await
            .map_err(|e| crate::error::Error::Request(e.to_string()))?;

        let results: SearchResponse = resp
            .json()
            .await
            .map_err(|e| crate::error::Error::Serialization(e.to_string()))?;

        Ok(results)
    }

    /// Perform a semantic search.
    pub async fn semantic_search(&self, query: &str, top_k: Option<u32>) -> Result<SearchResponse> {
        let req = SearchRequest {
            query: query.to_string(),
            top_k,
            threshold: None,
            mode: Some("vector".to_string()),
        };

        let url = format!("{}/api/v1/search", self.base_url);
        let resp = reqwest::Client::new()
            .post(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .json(&req)
            .send()
            .await
            .map_err(|e| crate::error::Error::Request(e.to_string()))?;

        let results: SearchResponse = resp
            .json()
            .await
            .map_err(|e| crate::error::Error::Serialization(e.to_string()))?;

        Ok(results)
    }
}
