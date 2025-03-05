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
      devShells.x86_64-linux.default =
        let
          pkgs = nixpkgs.legacyPackages.x86_64-linux;
          python = pkgs.python3;

          arg = project.renderers.withPackages {
            inherit python;
            extras = [
              "docs"
              "tests"
            ];
          };
          pythonEnv = python.withPackages arg;
        in
        pkgs.mkShell {
          packages = [
            pythonEnv
            pkgs.hatch
            pkgs.typst
          ];
          env.LAST_MODIFIED = self.lastModifiedDate;
        };

      packages.x86_64-linux = {
        inherit (pkgs.python3.pkgs) sphinxcontrib-typstbuilder;
        default = self.packages.x86_64-linux.sphinxcontrib-typstbuilder;
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

                sphinxBuilders = ["html" "typst"];

                env.LAST_MODIFIED = self.lastModifiedDate;
              });
          })
        ];
      };
    };
}
