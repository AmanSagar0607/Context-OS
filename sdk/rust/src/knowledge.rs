use serde::{Deserialize, Serialize};

use crate::error::Result;

/// Knowledge entity.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KnowledgeEntity {
    pub id: String,
    pub name: String,
    #[serde(rename = "type")]
    pub entity_type: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub properties: Option<std::collections::HashMap<String, String>>,
    pub created_at: String,
}

/// Knowledge relationship.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KnowledgeRelationship {
    pub id: String,
    pub source_id: String,
    pub target_id: String,
    #[serde(rename = "type")]
    pub relationship_type: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub properties: Option<std::collections::HashMap<String, String>>,
    pub weight: f64,
}

/// Knowledge query request.
#[derive(Debug, Serialize)]
pub struct KnowledgeQueryRequest {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub entity_name: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub entity_type: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_depth: Option<u32>,
}

/// Knowledge query response.
#[derive(Debug, Deserialize)]
pub struct KnowledgeQueryResponse {
    pub entities: Vec<KnowledgeEntity>,
    pub relationships: Vec<KnowledgeRelationship>,
}

/// Knowledge service.
pub struct KnowledgeService {
    base_url: String,
    api_key: String,
}

impl KnowledgeService {
    pub(crate) fn new(base_url: String, api_key: String) -> Self {
        KnowledgeService { base_url, api_key }
    }

    /// Add a knowledge entity.
    pub async fn add_entity(&self, entity: &KnowledgeEntity) -> Result<KnowledgeEntity> {
        let url = format!("{}/api/v1/knowledge/entities", self.base_url);
        let resp = reqwest::Client::new()
            .post(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .json(entity)
            .send()
            .await
            .map_err(|e| crate::error::Error::Request(e.to_string()))?;

        let result: KnowledgeEntity = resp
            .json()
            .await
            .map_err(|e| crate::error::Error::Serialization(e.to_string()))?;

        Ok(result)
    }

    /// Query the knowledge graph.
    pub async fn query(&self, entity_name: Option<&str>, max_depth: Option<u32>) -> Result<KnowledgeQueryResponse> {
        let req = KnowledgeQueryRequest {
            entity_name: entity_name.map(|s| s.to_string()),
            entity_type: None,
            max_depth,
        };

        let url = format!("{}/api/v1/knowledge/query", self.base_url);
        let resp = reqwest::Client::new()
            .post(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .json(&req)
            .send()
            .await
            .map_err(|e| crate::error::Error::Request(e.to_string()))?;

        let result: KnowledgeQueryResponse = resp
            .json()
            .await
            .map_err(|e| crate::error::Error::Serialization(e.to_string()))?;

        Ok(result)
    }
}
