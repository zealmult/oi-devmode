# oi-devmode

A lightweight developer logging filter designed for Open WebUI / OpenAI-compatible middleware.
It provides clean, structured, auto-formatted logs for:
	•	Incoming requests (INLET)
	•	Streaming responses (STREAM)
	•	Final assistant messages (OUTLET)

The V3 version introduces full compatibility with mixed event types — handling both
dict (frontend events) and bytes (API streaming events) without breaking the stream pipeline.

⸻

✨ Features

🔍 Developer Logging (Toggle Anytime)

Enable or disable detailed logging using a simple boolean switch.
When disabled, the middleware stays completely silent and cost-free.

📥 INLET Logging (User Requests)

Captures the latest incoming user message, including optional display of the entire __user__ dictionary.

📤 OUTLET Logging (Saved Responses)

Captures the assistant’s final response before saving to frontend.

📡 STREAM Logging (Real-time AI Output)

Supports both:
	•	Frontend delta (dict format)
	•	OpenAI API streaming chunks (bytes format)

Automatically detects type and logs appropriately, ensuring compatibility with custom models, proxies, and unusual streaming formats.

🔧 Configurable Valves

Control logging behavior with fine-grained options:
	•	enabled
	•	log_inlet
	•	log_stream
	•	log_outlet
	•	log_user_info
	•	truncate_message
	•	priority

⸻

📦 Installation

Add the Filter class into your Open WebUI plugin or Python middleware.

your_project/
└── filters/
    └── oi_devmode.py

Import it in your filter registry:

from filters.oi_devmode import Filter

Open WebUI will automatically load it.

⸻

🛠 Usage

Enable logging temporarily

filter = Filter()
filter.valves.enabled = True

Disable after debugging

filter.valves.enabled = False

Truncate long messages (optional)

filter.valves.truncate_message = 200


⸻

🧪 Example Log Output

------------------------------ [DEV_LOGGER | INLET] ------------------------------
USER: test@example.com (Role: admin)
MODEL: gpt-4.1
MESSAGE (Role: user):
Hello, can you help me debug this?

__USER__ dictionary details:
{
  "email": "test@example.com",
  "role": "admin"
}
------------------------------------------------------------------------------

STREAM logs:

[DEV_LOGGER | STREAM] (Dict) AI streaming: Sure, let me check...

Or bytes-format API:

[DEV_LOGGER | STREAM] (Bytes) AI streaming: {"delta":{"content":"Hello"}}


⸻

📘 API Summary

inlet()

Logs incoming user messages.

stream()

Logs every streamed partial output from the model.

outlet()

Logs the final assistant message and metadata.

All hooks return the original event unchanged, preserving pipeline integrity.

⸻

🧭 When to Use This

✔ Debugging custom models
✔ Developing new filters or pipelines
✔ Tracing AI answers in detail
✔ Monitoring user requests during testing
✔ Capturing malformed API streaming events

⸻

🚫 When NOT to Use

✖ Production (unless you purposely want verbose logs)
✖ Handling sensitive user info (remember log_user_info=True)
✖ High-throughput workloads (log spam may degrade performance)

⸻

🤝 Contributing

Pull requests and improvements are welcome!
Submit issues and ideas via GitHub.

⸻

❤️ Support the Project

If this tool improves your workflow, consider supporting:

https://breathai.top/

	•	或者想我帮你创建 PyPI 发布版本

我也能继续帮你。
