package dev.contextos;

import java.util.List;

/**
 * Crawl result.
 */
public class CrawlResult {
    private String id;
    private String url;
    private String title;
    private String content;
    private List<String> links;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getUrl() { return url; }
    public void setUrl(String url) { this.url = url; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }

    public List<String> getLinks() { return links; }
    public void setLinks(List<String> links) { this.links = links; }
}
