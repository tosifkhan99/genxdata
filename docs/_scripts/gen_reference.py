from pathlib import Path
import mkdocs_gen_files

SECTIONS: list[tuple[str, str]] = [
    ("strategies", "core/strategies"),
    ("writers", "core/writers"),
    ("processors", "core/processors"),
]

for section, rel_path in SECTIONS:
    src_dir = Path(rel_path)
    if not src_dir.exists():
        continue

    entries: list[tuple[str, str]] = []

    for py_file in sorted(src_dir.glob("*.py")):
        if py_file.stem == "__init__":
            continue
        module_name = py_file.with_suffix("").as_posix().replace("/", ".")
        out_path = Path("reference") / section / f"{py_file.stem}.md"
        with mkdocs_gen_files.open(out_path, "w") as fd:
            fd.write(f"# {py_file.stem}\n\n")
            fd.write(f"::: {module_name}\n")
        mkdocs_gen_files.set_edit_path(out_path, py_file)
        entries.append((py_file.stem, out_path.as_posix()))

    if entries:
        index_path = Path("reference") / section / "index.md"
        with mkdocs_gen_files.open(index_path, "w") as fd:
            fd.write(f"# {section.capitalize()}\n\n")
            for title, path in entries:
                fd.write(f"- [{title}]({Path(path).name})\n")
        mkdocs_gen_files.set_edit_path(index_path, None)
