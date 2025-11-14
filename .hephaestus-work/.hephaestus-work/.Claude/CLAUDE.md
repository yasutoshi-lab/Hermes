# Hephaestus Multi-Agent System

This is a Hephaestus multi-agent workspace. You are part of a collaborative system with Master and Worker agents working together.

## Project Structure

```
.hephaestus-work/
├── .Claude/              # Agent configuration files
│   ├── master/          # Master agent specific configs
│   └── worker/          # Worker agent specific configs
├── tasks/               # Task management
│   ├── pending/         # Tasks waiting to be assigned
│   ├── in_progress/     # Currently executing tasks
│   └── completed/       # Finished tasks
├── communication/       # Inter-agent communication
│   ├── master_to_worker/  # Master → Worker messages
│   └── worker_to_master/  # Worker → Master messages
├── logs/                # Agent logs
├── cache/               # Cached data and state
├── checkpoints/         # Task checkpoints
└── progress/            # Progress tracking
```

## Communication Protocol

### File-Based Messaging
- Use markdown files in `communication/` directories
- Filename format: `{timestamp}_{from}_{to}_{task_id}.md`
- Include task ID, priority, and clear instructions

### Task Files
- Tasks are stored in `tasks/` with status directories
- Task file format: `task_{id}.yaml` or `task_{id}.md`
- Move tasks between directories to update status

## Best Practices

1. **Clear Communication**: Write detailed, actionable messages
2. **Status Updates**: Regularly update task status
3. **Checkpointing**: Save progress frequently
4. **Error Handling**: Log errors and notify other agents
5. **Idempotency**: Design tasks to be safely retryable
