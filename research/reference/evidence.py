"""Streaming collector. It observes events, never Oracle predicates/labels."""
from __future__ import annotations
from wire import CHANNELS, channel, digest

class Collector:
    def __init__(self, context: dict[str, str]):
        self.context = context.copy()
        self.records = {'schema': 'isa-evidence-1', 'context_digest': digest(context), 'start_tick': context['start_tick']}
        self.program_registration = ''
        self.event_count = 0

    def observe(self, channel_name: str, fields: dict[str, str]) -> None:
        if channel_name not in CHANNELS or any(k in self.records for k in fields):
            raise ValueError('duplicate/unknown event')
        self.records.update(fields)
        self.event_count += 1
        if channel_name == 'program':
            # Separate monitor binding to the program actually registered at run time.
            self.program_registration = digest(fields)

    def finish(self, replacements: dict[str, str] | None = None, omit: tuple[str, ...] = ()) -> tuple[dict[str, str], dict[str, str]]:
        records = self.records.copy()
        records['finish_tick'] = str(int(self.context['start_tick']) + self.event_count)
        # A generic faulty serialization transform can be injected; no fault-name branch.
        for k, v in (replacements or {}).items():
            records[k] = v
        records = {k: v for k, v in records.items() if k not in omit}
        seal = {'schema': 'isa-collector-seal-1', 'context_digest': digest(self.context),
                'collector': self.context['collector'], 'monitor': self.context['monitor'],
                'registered_program_digest': self.program_registration,
                'start_tick': self.context['start_tick'], 'finish_tick': records['finish_tick']}
        for name in CHANNELS:
            seal['digest.'+name] = digest(channel(records, name))
            if name != 'lineage':
                seal['monitor_digest.'+name] = digest(channel(self.records, name))
        # Seal is an independently supplied collector checkpoint, not self-authenticating JSON.
        return records, seal
