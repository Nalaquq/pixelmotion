"""Catch labels that collide with other labels or sit on top of lines/arrows.

These are the recurring slide bugs from the course style notes: labels that
look fine in the last frame but collide mid-animation, superseded labels left
on screen, and labels drawn on the vector they describe.
"""

from dataclasses import dataclass, field

MIN_ALPHA = 0.3     # ignore labels still fading in / out
SHRINK_PX = 2       # tolerate glyph boxes that merely touch


@dataclass
class OverlapIssue:
    kind: str       # "text/text" or "text/line"
    a: str
    b: str
    frames: list = field(default_factory=list)

    def __str__(self):
        f = self.frames
        span = f"frame {f[0]}" if len(f) == 1 else f"frames {f[0]}-{f[-1]}"
        return f"[{self.kind}] {self.a!r} overlaps {self.b!r} ({span}, {len(f)} frames)"


class OverlapReport:
    def __init__(self):
        self._issues = {}

    def add(self, frame, kind, a, b):
        key = (kind, a, b)
        if key not in self._issues:
            self._issues[key] = OverlapIssue(kind, a, b)
        self._issues[key].frames.append(frame)

    @property
    def issues(self):
        return list(self._issues.values())

    def __bool__(self):
        return bool(self._issues)

    def __str__(self):
        if not self._issues:
            return "No overlaps."
        return "\n".join(str(i) for i in self.issues)


def _visible_texts(texts, renderer):
    out = []
    for t in texts:
        s = t.get_text()
        if not s.strip() or not t.get_visible():
            continue
        a = t.get_alpha()
        if a is not None and a < MIN_ALPHA:
            continue
        bb = t.get_window_extent(renderer)
        if bb.width <= 0 or bb.height <= 0:
            continue
        box = (bb.x0 + SHRINK_PX, bb.y0 + SHRINK_PX, bb.x1 - SHRINK_PX, bb.y1 - SHRINK_PX)
        out.append((s, box))
    return out


def _boxes_intersect(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def _segment_hits_box(p, q, box):
    """Liang-Barsky clip of segment pq against an axis-aligned box."""
    x0, y0, x1, y1 = box
    t0, t1 = 0.0, 1.0
    d = q - p
    for pk, qk in ((-d[0], p[0] - x0), (d[0], x1 - p[0]),
                   (-d[1], p[1] - y0), (d[1], y1 - p[1])):
        if pk == 0:
            if qk < 0:
                return False
        else:
            r = qk / pk
            if pk < 0:
                t0 = max(t0, r)
            else:
                t1 = min(t1, r)
            if t0 > t1:
                return False
    return True


def check_frame(ctx, renderer, frame, report):
    texts = _visible_texts(ctx.drawn_texts, renderer)
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            (sa, ba), (sb, bb) = texts[i], texts[j]
            if _boxes_intersect(ba, bb):
                report.add(frame, "text/text", *sorted((sa, sb)))
    for ax, pts, label in ctx.segments:
        disp = ax.transData.transform(pts)
        for s, box in texts:
            for p, q in zip(disp[:-1], disp[1:]):
                if _segment_hits_box(p, q, box):
                    report.add(frame, "text/line", s, label or "line")
                    break
