from colour import Color

from chalk.combinators import concat
from chalk.shapes import Path, circle, text
from chalk.shapes.segment import seg
from chalk.transform import V2, origin
from chalk.types import Diagram


RED = Color("red")
BLUE = Color("blue")


def show_origin(self: Diagram) -> Diagram:
    "Add a red dot at the origin of a diagram for debugging."

    envelope = self.get_envelope()
    if envelope.is_empty:
        return self
    origin_size = max(0.1, min(envelope.height, envelope.width) / 50)
    origin = circle(origin_size).line_color(RED)
    return self + origin


def show_envelope(
    self: Diagram, phantom: bool = False, angle: int = 45
) -> Diagram:
    """Add red envelope to diagram for debugging.

    Args:
        self (Diagram) : Diagram
        phantom (bool): Don't include debugging in the envelope
        angle (int): Angle increment to show debugging lines.

    Returns:
        Diagram
    """

    self.show_origin()
    envelope = self.get_envelope()
    if envelope.is_empty:
        return self
    outer: Diagram = (
        Path.from_points(list(envelope.to_path(angle)))
        .stroke()
        .fill_opacity(0)
        .line_color(RED)
    )
    outer += (
        concat([seg(y).stroke() for (x, y) in envelope.to_segments(angle)])
        .line_color(RED)
        .dashing([0.01, 0.01], 0)
    )

    new = self + outer
    if phantom:
        new = new.with_envelope(self)
    return new


def show_beside(self: Diagram, other: Diagram, direction: V2) -> Diagram:
    "Add blue normal line to show placement of combination."

    envelope1 = self.get_envelope()
    envelope2 = other.get_envelope()
    v1 = envelope1.envelope_v(direction)
    one: Diagram = (
        Path.from_points([origin, v1])
        .stroke()
        .line_color(RED)
        .dashing([0.01, 0.01], 0)
        .line_width(0.01)
    )
    v2 = envelope2.envelope_v(-direction)
    two: Diagram = (
        Path.from_points([origin, v2])
        .stroke()
        .line_color(RED)
        .dashing([0.01, 0.01], 0)
        .line_width(0.01)
    )
    split: Diagram = (
        Path.from_points(
            [
                v1 + direction.perpendicular(),
                v1 - direction.perpendicular(),
            ]
        )
        .stroke()
        .line_color(BLUE)
        .line_width(0.02)
    )
    one = (self.show_origin() + one + split).with_envelope(self)
    two = (other.show_origin() + two).with_envelope(other)
    return one.beside(two, direction)


def show_labels(self: Diagram, font_size: int = 1) -> Diagram:
    """Shows the labels of all named subdiagrams of a diagram at their
    corresponding origin."""
    for name, subs in self.get_sub_map().items():
        for sub in subs:
            n = str(name)
            p = sub.get_location()
            self = self + text(n, font_size).fill_color(RED).translate_by(p)
    return self
