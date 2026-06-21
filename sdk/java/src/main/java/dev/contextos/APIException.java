package dev.contextos;

/**
 * API exception.
 */
public class APIException extends RuntimeException {
    private final int statusCode;
    private final String message;

    public APIException(int statusCode, String message) {
        super("API error " + statusCode + ": " + message);
        this.statusCode = statusCode;
        this.message = message;
    }

    public int getStatusCode() {
        return statusCode;
    }

    @Override
    public String getMessage() {
        return message;
    }
}
