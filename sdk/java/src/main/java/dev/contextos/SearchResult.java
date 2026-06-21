package dev.contextos;

/**
 * Search result.
 */
public class SearchResult {
    private Memory memory;
    private double score;
    private int rank;

    public Memory getMemory() { return memory; }
    public void setMemory(Memory memory) { this.memory = memory; }

    public double getScore() { return score; }
    public void setScore(double score) { this.score = score; }

    public int getRank() { return rank; }
    public void setRank(int rank) { this.rank = rank; }
}
