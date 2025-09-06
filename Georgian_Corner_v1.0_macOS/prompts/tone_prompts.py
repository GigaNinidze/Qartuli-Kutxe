"""Tone-specific adjectives for Georgian advertisement generation.

Each tone keyword maps to its Georgian description that will be substituted
into the base prompt as the ``{tone}`` placeholder.
"""

TONES: dict[str, str] = {
    "პროფესიონალური": "პროფესიონალური",
    "მეგობრული": "მეგობრული",
    "სასწრაფო": "სასწრაფო და დამარწმუნებელი",
    "ელეგანტური": "მაღალი კლასის და ელეგანტური",
    "ყოველდღიური/უბრალო": "უბრალო, ყოველდღიური",
}
