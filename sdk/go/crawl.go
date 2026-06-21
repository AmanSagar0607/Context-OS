package contextos

import (
	"context"
	"encoding/json"
	"fmt"
)

// CrawlRequest is the request to crawl a URL.
type CrawlRequest struct {
	URL      string            `json:"url"`
	Depth    int               `json:"depth,omitempty"`
	MaxPages int               `json:"max_pages,omitempty"`
	Extract  bool              `json:"extract,omitempty"`
	Options  map[string]string `json:"options,omitempty"`
}

// CrawlResult represents a crawl result.
type CrawlResult struct {
	ID       string            `json:"id"`
	URL      string            `json:"url"`
	Title    string            `json:"title"`
	Content  string            `json:"content"`
	Links    []string          `json:"links,omitempty"`
	Metadata map[string]string `json:"metadata,omitempty"`
}

// CrawlResponse is the response from crawl.
type CrawlResponse struct {
	Result  CrawlResult `json:"result"`
	Status  string      `json:"status"`
	Message string      `json:"message,omitempty"`
}

// CrawlService handles crawl operations.
type CrawlService struct {
	client *Client
}

// Crawl crawls a URL.
func (s *CrawlService) Crawl(ctx context.Context, req *CrawlRequest) (*CrawlResponse, error) {
	var result CrawlResponse
	body, err := s.client.doRequest(ctx, "POST", "/api/v1/crawl", req)
	if err != nil {
		return nil, err
	}
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}
	return &result, nil
}

// Map crawls and maps a website.
func (s *CrawlService) Map(ctx context.Context, url string, maxPages int) (*CrawlResponse, error) {
	req := &CrawlRequest{
		URL:      url,
		MaxPages: maxPages,
	}
	return s.Crawl(ctx, req)
}

// Extract extracts content from a URL.
func (s *CrawlService) Extract(ctx context.Context, url string) (*CrawlResponse, error) {
	req := &CrawlRequest{
		URL:     url,
		Extract: true,
	}
	return s.Crawl(ctx, req)
}
