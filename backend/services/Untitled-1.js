fetch('/api/automations/debug-extract-simple', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ channel_id: 'UCX6OQ3DkcsbYNE6H8uQQuVA' })
})
.then(r => r.json())
.then(console.log)