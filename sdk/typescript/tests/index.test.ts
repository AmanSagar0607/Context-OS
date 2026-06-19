import { describe, it, expect } from "vitest";
import { ContextAI, MemoryType, ImportanceLevel } from "../src/index.js";

describe("ContextAI", () => {
  it("should initialize with defaults", () => {
    const client = new ContextAI();
    expect(client).toBeDefined();
    expect(client.memory).toBeDefined();
    expect(client.search).toBeDefined();
    expect(client.crawl).toBeDefined();
    expect(client.knowledge).toBeDefined();
  });

  it("should initialize with custom options", () => {
    const client = new ContextAI({
      baseUrl: "http://custom:9000",
      apiKey: "test-key",
    });
    expect(client).toBeDefined();
  });
});

describe("Memory Types", () => {
  it("should have correct enum values", () => {
    expect(MemoryType.EPISODIC).toBe("episodic");
    expect(MemoryType.SEMANTIC).toBe("semantic");
    expect(MemoryType.PROCEDURAL).toBe("procedural");
  });

  it("should have correct importance levels", () => {
    expect(ImportanceLevel.LOW).toBe("low");
    expect(ImportanceLevel.MEDIUM).toBe("medium");
    expect(ImportanceLevel.HIGH).toBe("high");
    expect(ImportanceLevel.CRITICAL).toBe("critical");
  });
});

describe("Memory Client", () => {
  it("should have all methods", () => {
    const client = new ContextAI();
    expect(typeof client.memory.add).toBe("function");
    expect(typeof client.memory.get).toBe("function");
    expect(typeof client.memory.update).toBe("function");
    expect(typeof client.memory.delete).toBe("function");
    expect(typeof client.memory.search).toBe("function");
    expect(typeof client.memory.context).toBe("function");
    expect(typeof client.memory.list).toBe("function");
    expect(typeof client.memory.related).toBe("function");
  });
});

describe("Search Client", () => {
  it("should have all methods", () => {
    const client = new ContextAI();
    expect(typeof client.search.web).toBe("function");
    expect(typeof client.search.internal).toBe("function");
  });
});

describe("Crawl Client", () => {
  it("should have all methods", () => {
    const client = new ContextAI();
    expect(typeof client.crawl.scrape).toBe("function");
    expect(typeof client.crawl.crawl).toBe("function");
    expect(typeof client.crawl.map).toBe("function");
    expect(typeof client.crawl.extract).toBe("function");
  });
});

describe("Knowledge Client", () => {
  it("should have all methods", () => {
    const client = new ContextAI();
    expect(typeof client.knowledge.createEntity).toBe("function");
    expect(typeof client.knowledge.getEntity).toBe("function");
    expect(typeof client.knowledge.deleteEntity).toBe("function");
    expect(typeof client.knowledge.createRelationship).toBe("function");
    expect(typeof client.knowledge.getGraph).toBe("function");
    expect(typeof client.knowledge.search).toBe("function");
  });
});