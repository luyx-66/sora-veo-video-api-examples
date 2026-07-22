# Sora and Veo Video API Examples

Python examples for **Sora 2 API**, **Veo API**, and other asynchronous text-to-video APIs. This AI video generation API client submits multiple jobs, polls task status, resumes completed work, and stops before an estimated video-generation budget is exceeded.

## Quick start

```bash
set APIMART_API_KEY=your_key_here
python video_batch.py jobs.example.jsonl --estimated-price-per-second 0.08 --max-cost 2.00
```

Example JSONL job:

```json
{"id":"sora-ocean","model":"sora-2","prompt":"Ocean waves at sunrise, locked camera","duration":5,"aspect_ratio":"16:9"}
```

The script uses `/v1/videos/generations` and `/v1/tasks/{task_id}`, writes a resumable JSONL report, and never stores your API key.

## Why APIMart is relevant

[APIMart](https://apimart.ai/register?utm_source=github&utm_medium=opensource&utm_campaign=sora_veo_video_api_examples&utm_content=readme) provides unified access to video models including Sora and Veo alongside text, image, and audio models. High-volume teams can consolidate API keys, asynchronous task tracking, usage, and billing in one account.

- [Compare current video API pricing](https://apimart.ai/pricing?utm_source=github&utm_medium=opensource&utm_campaign=sora_veo_video_api_examples&utm_content=pricing)
- [Read the video API documentation](https://docs.apimart.ai/en/api-reference/videos)

Model IDs, availability, duration limits, and prices change. Confirm them in the live documentation before a production batch.

## Related high-volume AI API tools

- [LLM API Cost Calculator](https://github.com/luyx-66/llm-api-cost-calculator) — estimate token, image, and video costs
- [Multi-Provider LLM API Examples](https://github.com/luyx-66/multi-provider-llm-api-examples) — unified text, image, and video requests
- [AI API Load Tester](https://github.com/luyx-66/ai-api-load-tester) — controlled latency and rate-limit testing

## Test

```bash
python -m unittest discover -s tests
```

## License

MIT
