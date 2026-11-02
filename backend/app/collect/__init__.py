"""Turn an official page into retained evidence (S01 collector seam).

Collection is deliberately the least clever part of the system: check the
source's access rules, fetch once, keep the readable text, hash it, and record
where it came from. A claim is only evidence if the exact text it quotes is in
the snapshot, so anything that rewrites or tidies page wording belongs here and
nowhere else.
"""
