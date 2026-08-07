#!/usr/bin/env python3
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

from validate_quiz import validate


CREAM = "#FDFAF5"
DARK = "#1C1410"
ORANGE = "#D97A3A"
BEIGE = "#8A7560"
GREEN = "#397A43"
RED = "#B83030"
LETTERS = "ABC"


def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def wrapped(draw, text, xy, max_chars, font_obj, fill, spacing=12, anchor=None):
    lines = textwrap.wrap(text, width=max_chars, break_long_words=False)
    draw.multiline_text(xy, "\n".join(lines), font=font_obj, fill=fill, spacing=spacing, anchor=anchor)


def canvas(size, label, title):
    image = Image.new("RGB", size, CREAM)
    draw = ImageDraw.Draw(image)
    width, height = size
    base = min(width, height)
    header_h = int(height * 0.16)
    draw.rectangle((0, 0, width, header_h), fill=DARK)
    draw.text((width // 2, int(header_h * 0.30)), "SOS MARÉCHAL-FERRANT", font=font(int(base * 0.028), True), fill=ORANGE, anchor="mm")
    draw.text((width // 2, int(header_h * 0.60)), label, font=font(int(base * 0.021), True), fill="#C9B89A", anchor="mm")
    wrapped(draw, title, (width // 2, int(header_h * 0.82)), 38 if width < height else 60, font(int(base * 0.027), True), CREAM, anchor="mm")
    return image, draw, header_h


def question_card(quiz, q, size):
    image, draw, header_h = canvas(size, q["id"], quiz["titre"])
    w, h = size
    base = min(w, h)
    y = header_h + int(h * 0.055)
    if q.get("action_urgente"):
        draw.rounded_rectangle((int(w*.08), y, int(w*.92), y+int(h*.085)), radius=24, fill="#FFE8E8", outline=RED, width=4)
        wrapped(draw, q["action_urgente"], (w//2, y+int(h*.043)), 38 if w < h else 64, font(int(base*.030), True), RED, anchor="mm")
        y += int(h*.115)
    wrapped(draw, q["question"], (int(w*.08), y), 34 if w < h else 58, font(int(base*.041), True), DARK, spacing=16)
    y += int(h * (0.20 if w < h else 0.13))
    for idx, choice in enumerate(q["choix"]):
        box_h = int(h * (0.095 if w < h else 0.11))
        draw.rounded_rectangle((int(w*.07), y, int(w*.93), y+box_h), radius=24, fill="white", outline="#E8D8C0", width=4)
        circle_x1 = int(w*.095)
        circle_x2 = circle_x1 + int(base*.065)
        draw.ellipse((circle_x1, y+int(box_h*.24), circle_x2, y+int(box_h*.76)), fill="#E8D8C0")
        draw.text(((circle_x1 + circle_x2)//2, y+box_h//2), LETTERS[idx], font=font(int(base*.026), True), fill=DARK, anchor="mm")
        wrapped(draw, choice, (int(w*.19), y+int(box_h*.22)), 38 if w < h else 67, font(int(base*.025), True), DARK, spacing=10)
        y += box_h + int(h * (0.018 if w < h else 0.015))
    footer_y = .86 if w < h else .95
    draw.text((w//2, int(h*footer_y)), "Choisissez A, B ou C · réponse dans 3 secondes", font=font(int(base*.021), True), fill=BEIGE, anchor="mm")
    return image


def answer_card(quiz, q, size):
    image, draw, header_h = canvas(size, "RÉPONSE", quiz["titre"])
    w, h = size
    base = min(w, h)
    letter = LETTERS[q["bonne_reponse"] - 1]
    diameter = int(base*.22)
    circle_x1 = (w - diameter) // 2
    circle_y1 = header_h + int(h*.045)
    draw.ellipse((circle_x1, circle_y1, circle_x1 + diameter, circle_y1 + diameter), fill=GREEN)
    draw.text((w//2, circle_y1 + diameter//2), letter, font=font(int(base*.10), True), fill="white", anchor="mm")
    y = header_h + int(h * (.22 if w < h else .30))
    wrapped(draw, q["choix"][q["bonne_reponse"]-1], (w//2, y), 34 if w < h else 58, font(int(base*.035), True), DARK, spacing=16, anchor="ma")
    draw.rounded_rectangle((int(w*.07), int(h*.53), int(w*.93), int(h*.82)), radius=28, fill="white", outline=ORANGE, width=4)
    wrapped(draw, q["explication"], (int(w*.11), int(h*.575)), 38 if w < h else 70, font(int(base*.026), False), DARK, spacing=14)
    warning_y = .82 if w < h else .89
    cta_y = .86 if w < h else .94
    draw.text((w//2, int(h*warning_y)), quiz["avertissement"], font=font(int(base*.018), True), fill=BEIGE, anchor="mm")
    draw.text((w//2, int(h*cta_y)), quiz["cta"], font=font(int(base*.023), True), fill=ORANGE, anchor="mm")
    return image


def intro_card(quiz, size):
    image, draw, header_h = canvas(size, quiz["serie"], quiz["titre"])
    w, h = size
    base = min(w, h)
    draw.text((w//2, int(h*.37)), "?", font=font(int(base*.22), True), fill=ORANGE, anchor="mm")
    wrapped(draw, f"{len(quiz['questions'])} questions pour tester votre regard", (w//2, int(h*.56)), 34 if w < h else 54, font(int(base*.045), True), DARK, anchor="ma")
    wrapped(draw, "Une question à la fois. Notez A, B ou C avant de voir la réponse.", (w//2, int(h*.72)), 40 if w < h else 66, font(int(base*.027)), BEIGE, anchor="ma")
    draw.text((w//2, int(h*.92)), quiz["avertissement"], font=font(int(base*.018), True), fill=BEIGE, anchor="mm")
    return image


def make_clip(still: Path, seconds: int, out: Path, size):
    subprocess.run([
        "ffmpeg", "-y", "-loop", "1", "-framerate", "30", "-i", str(still),
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
        "-vf", f"scale={size[0]}:{size[1]},format=yuv420p", "-t", str(seconds),
        "-c:v", "libx264", "-preset", "veryfast", "-r", "30", "-c:a", "aac",
        "-movflags", "+faststart", str(out)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def concat(clips, out):
    list_file = out.parent / f"{out.stem}_concat.txt"
    list_file.write_text("".join(f"file '{p.resolve()}'\n" for p in clips), encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(out)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    list_file.unlink()


def render(quiz_path: Path):
    quiz = validate(quiz_path)
    slug = quiz_path.stem
    root = Path(__file__).resolve().parents[1]
    out = root / "exports" / slug
    if out.exists():
        shutil.rmtree(out)
    (out / "carrousel").mkdir(parents=True)
    (out / "vertical").mkdir()
    (out / "youtube").mkdir()

    # Carrousel : une question et sa réponse par paire d'images.
    intro_card(quiz, (1080, 1350)).save(out / "carrousel" / "00_intro.png")
    for i, q in enumerate(quiz["questions"], 1):
        question_card(quiz, q, (1080, 1350)).save(out / "carrousel" / f"{i:02d}_question.png")
        answer_card(quiz, q, (1080, 1350)).save(out / "carrousel" / f"{i:02d}_reponse.png")

    # Une vidéo verticale autonome par question.
    vertical_clips = []
    for i, q in enumerate(quiz["questions"], 1):
        q_img = out / "vertical" / f"{i:02d}_question.png"
        a_img = out / "vertical" / f"{i:02d}_reponse.png"
        question_card(quiz, q, (1080, 1920)).save(q_img)
        answer_card(quiz, q, (1080, 1920)).save(a_img)
        q_clip = out / "vertical" / f"{i:02d}_q.mp4"
        a_clip = out / "vertical" / f"{i:02d}_a.mp4"
        make_clip(q_img, 10, q_clip, (1080, 1920))
        make_clip(a_img, 12, a_clip, (1080, 1920))
        reel = out / "vertical" / f"{i:02d}_{q['id']}_reel-short.mp4"
        concat([q_clip, a_clip], reel)
        vertical_clips.append(reel)
        q_clip.unlink(); a_clip.unlink()

    # Compilation YouTube horizontale.
    yt_clips = []
    intro = out / "youtube" / "00_intro.png"
    intro_card(quiz, (1920, 1080)).save(intro)
    intro_clip = out / "youtube" / "00_intro.mp4"
    make_clip(intro, 6, intro_clip, (1920, 1080)); yt_clips.append(intro_clip)
    for i, q in enumerate(quiz["questions"], 1):
        q_img = out / "youtube" / f"{i:02d}_question.png"
        a_img = out / "youtube" / f"{i:02d}_reponse.png"
        question_card(quiz, q, (1920, 1080)).save(q_img)
        answer_card(quiz, q, (1920, 1080)).save(a_img)
        q_clip = out / "youtube" / f"{i:02d}_q.mp4"
        a_clip = out / "youtube" / f"{i:02d}_a.mp4"
        make_clip(q_img, 10, q_clip, (1920, 1080)); make_clip(a_img, 12, a_clip, (1920, 1080))
        yt_clips.extend([q_clip, a_clip])
    concat(yt_clips, out / "youtube" / "quiz-complet-youtube.mp4")
    for clip in yt_clips:
        clip.unlink()

    publication = [f"# {quiz['titre']}", "", quiz["cta"], ""]
    for q in quiz["questions"]:
        publication += [f"## {q['id']}", q["question"], "", quiz["avertissement"], ""]
    (out / "textes-publication.md").write_text("\n".join(publication), encoding="utf-8")
    (out / "sources.yaml").write_text(yaml.safe_dump({"sources": quiz.get("sources", [])}, allow_unicode=True, sort_keys=False), encoding="utf-8")
    for temporary in (out / "vertical").glob("[0-9][0-9]_[qa].mp4"):
        temporary.unlink(missing_ok=True)
    print(out)


if __name__ == "__main__":
    render(Path(sys.argv[1]))
