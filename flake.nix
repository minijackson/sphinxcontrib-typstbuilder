{
  description = "Build PDF from your Sphinx documentation using Typst";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    pyproject-nix = {
      url = "github:nix-community/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      pyproject-nix,
      ...
    }:
    let
      project = pyproject-nix.lib.project.loadPyproject { projectRoot = ./.; };
      pkgs = import nixpkgs {
        system = "x86_64-linux";
        overlays = [ self.overlays.default ];
      };
    in
    {
      packages.x86_64-linux = {
        inherit (pkgs.python3.pkgs) sphinxcontrib-typstbuilder;
        default = self.packages.x86_64-linux.sphinxcontrib-typstbuilder;
      };

      checks.x86_64-linux = {
        sphinx-test-root = pkgs.callPackage ./tests/sphinx-test-root { };
      };

      overlays.default = _final: prev: {
        pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
          (final: _prev: {
            sphinxcontrib-typstbuilder =
              let
                inherit (final) python;
                attrs = project.renderers.buildPythonPackage {
                  inherit python;
                  extras = [ "docs" ];
                  extrasAttrMappings.docs = "nativeBuildInputs";
                };
              in
              (python.pkgs.buildPythonPackage attrs).overrideAttrs (old: {
                nativeBuildInputs = (old.nativeBuildInputs or [ ]) ++ [
                  python.pkgs.sphinxHook
                  python.pkgs.pytestCheckHook
                ];

                sphinxBuilders = [
                  "html"
                  "typst"
                ];

                env.LAST_MODIFIED = self.lastModifiedDate;
              });
          })
        ];
      };
    };
}
