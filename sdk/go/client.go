// Package contextos provides a Go SDK for ContextOS.
//
// Usage:
//
//	client := contextos.NewClient("https://api.contextos.dev", "your-api-key")
//
//	// Add memory
//	memory, err := client.Memory.Add(ctx, &contextos.AddMemoryRequest{
//	    Content: "Important information",
//	    Type:    contextos.MemoryTypeFact,
//	})
//
//	// Search
//	results, err := client.Search.Search(ctx, &contextos.SearchRequest{
//	    Query: "important information",
//	})
package contextos

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

const (
	defaultBaseURL = "https://api.contextos.dev"
	defaultTimeout = 30 * time.Second
)

// Client is the ContextOS API client.
type Client struct {
	baseURL    string
	apiKey     string
	httpClient *http.Client
	Memory     *MemoryService
	Search     *SearchService
	Crawl      *CrawlService
	Knowledge  *KnowledgeService
}

// NewClient creates a new ContextOS client.
func NewClient(baseURL, apiKey string) *Client {
	if baseURL == "" {
		baseURL = defaultBaseURL
	}

	client := &Client{
		baseURL: baseURL,
		apiKey:  apiKey,
		httpClient: &http.Client{
			Timeout: defaultTimeout,
		},
	}

	client.Memory = &MemoryService{client: client}
	client.Search = &SearchService{client: client}
	client.Crawl = &CrawlService{client: client}
	client.Knowledge = &KnowledgeService{client: client}

	return client
}

// APIError represents an API error.
type APIError struct {
	StatusCode int    `json:"status_code"`
	Message    string `json:"message"`
	Detail     string `json:"detail,omitempty"`
}

func (e *APIError) Error() string {
	return fmt.Sprintf("API error %d: %s", e.StatusCode, e.Message)
}

// doRequest performs an HTTP request.
func (c *Client) doRequest(ctx context.Context, method, path string, body interface{}) ([]byte, error) {
	url := c.baseURL + path

	var bodyReader io.Reader
	if body != nil {
		jsonBytes, err := json.Marshal(body)
		if err != nil {
			return nil, fmt.Errorf("failed to marshal body: %w", err)
		}
		bodyReader = bytes.NewReader(jsonBytes)
	}

	req, err := http.NewRequestWithContext(ctx, method, url, bodyReader)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+c.apiKey)

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode >= 400 {
		var apiErr APIError
		if err := json.Unmarshal(respBody, &apiErr); err != nil {
			return nil, &APIError{
				StatusCode: resp.StatusCode,
				Message:    string(respBody),
			}
		}
		apiErr.StatusCode = resp.StatusCode
		return nil, &apiErr
	}

	return respBody, nil
}
