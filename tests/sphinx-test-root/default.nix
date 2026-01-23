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
    ./skip-extensions.patch
    ./temp-term-list.patch
    ./typst-math.patch
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
