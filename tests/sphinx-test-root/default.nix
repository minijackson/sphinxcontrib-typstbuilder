{
  stdenvNoCC,
  sphinx,
  python3Packages,
  typst,
}:

stdenvNoCC.mkDerivation (final: {
  name = "typst-sphinx-test-root";

  inherit (sphinx) src;

  sourceRoot = "${final.src.name}/tests/roots/test-root";

  patches = [
    # Due to extensions not supporting the Typst
    ./skip-extensions.patch

    # Due to what I think is a Sphinx bug,
    # see: https://github.com/sphinx-doc/sphinx/pull/14288
    ./skip-citation-refs.patch

    # We currently don't support multiple terms
    ./temp-term-list.patch

    # We currently only support Typst math
    ./typst-math.patch

    # Due to a Typst bug when embedding an empty file
    ./includes.patch
  ];

  nativeBuildInputs = [
    sphinx
    python3Packages.sphinxcontrib-typstbuilder
    (typst.withPackages (
      p: with p; [
        gentle-clues_1_2_0
        linguify_0_4_2
      ]
    ))
  ];

  buildPhase = ''
    runHook preBuild
    sphinx-build -M typst "." "_build"
    runHook postBuild
  '';

  installPhase = ''
    runHook preInstall
    typst compile _build/typst/main/main.typ
    install -Dt $out _build/typst/main/main.typ _build/typst/main/main.pdf
    runHook postInstall
  '';
})
