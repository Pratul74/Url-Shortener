import { createShortUrl } from "../api/url";

export async function shortenUrl(data) {
    return createShortUrl(data);
}

export default shortenUrl;
