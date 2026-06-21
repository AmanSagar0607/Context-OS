use serde::{Deserialize, Serialize};

use crate::error::Result;

/// Memory type.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MemoryType {
    #[serde(rename = "fact")]
    Fact,
    #[serde(rename = "insight")]
    Insight,
    #[serde(rename = "code")]
    Code,
    #[serde(rename = "decision")]
    Decision,
    #[serde(rename = "error")]
    Error,
    #[serde(rename = "learning")]
    Learning,
    #[serde(rename = "context")]
    Context,
    #[serde(rename = "conversation")]
    Conversation,
}

/// Memory entry.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Memory {
    pub id: String,
    pub content: String,
    #[serde(rename = "type")]
    pub memory_type: MemoryType,
    pub scope: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub scope_id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub metadata: Option<std::collections::HashMap<String, String>>,
    pub importance: f64,
    pub decay: f64,
    pub access_count: u32,
    pub created_at: String,
    pub updated_at: String,
}

/// Add memory request.
#[derive(Debug, Serialize)]
pub struct AddMemoryRequest {
    pub content: String,
    #[serde(rename = "type")]
    pub memory_type: MemoryType,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub scope: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub scope_id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub metadata: Option<std::collections::HashMap<String, String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub importance: Option<f64>,
}

/// Search memory request.
#[derive(Debug, Serialize)]
pub struct SearchMemoryRequest {
    pub query: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub r#type: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub scope: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub scope_id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub top_k: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub threshold: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub filters: Option<Vec<String>>,
}

/// Search result.
#[derive(Debug, Deserialize)]
pub struct SearchResult {
    pub memory: Memory,
    pub score: f64,
    pub rank: u32,
}

/// Search response.
#[derive(Debug, Deserialize)]
pub struct SearchResponse {
    pub results: Vec<SearchResult>,
    pub query: String,
    pub total_hits: u32,
}

/// Memory service.
pub struct MemoryService {
    base_url: String,
    api_key: String,
}

impl MemoryService {
    pub(crate) fn new(base_url: String, api_key: String) -> Self {
        MemoryService { base_url, api_key }
    }

    /// Add a new memory.
    pub async fn add(&self, content: &str) -> Result<Memory> {
        let req = AddMemoryRequest {
            content: content.to_string(),
            memory_type: MemoryType::Fact,
            scope: None,
            scope_id: None,
            metadata: None,
            importance: None,
        };

        let url = format!("{}/api/v1/memory", self.base_url);
        let resp = reqwest::Client::new()
            .post(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .json(&req)
            .send()
            .await
            .map_err(|e| crate::error::Error::Request(e.to_string()))?;

        let memory: Memory = resp
            .json()
            .await
            .map_err(|e| crate::error::Error::Serialization(e.to_string()))?;

        Ok(memory)
    }

    /// Get a memory by ID.
    pub async fn get(&self, memory_id: &str) -> Result<Memory> {
        let url = format!("{}/api/v1/memory/{}", self.base_url, memory_id);
        let resp = reqwest::Client::new()
            .get(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .send()
            .await
            .map_err(|e| crate::error::Error::Request(e.to_string()))?;

        let memory: Memory = resp
            .json()
            .await
            .map_err(|e| crate::error::Error::Serialization(e.to_string()))?;

        Ok(memory)
    }

    /// Delete a memory.
    pub async fn delete(&self, memory_id: &str) -> Result<()> {
        let url = format!("{}/api/v1/memory/{}", self.base_url, memory_id);
        reqwest::Client::new()
            .delete(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .send()
            .await
            .map_err(|e| crate::error::Error::Request(e.to_string()))?;

        Ok(())
    }

    /// Search memories.
    pub async fn search(&self, query: &str, top_k: Option<u32>) -> Result<SearchResponse> {
        let req = SearchMemoryRequest {
            query: query.to_string(),
            r#type: None,
            scope: None,
            scope_id: None,
            top_k,
            threshold: None,
            filters: None,
        };

        let url = format!("{}/api/v1/memory/search", self.base_url);
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
