{ isDevelopment ? true }:

let
  # Update packages with `nixpkgs-update` command
  pkgs = import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/1afc5440469f94e7ed26e8648820971b102afdc3.tar.gz") { };

  pythonLibs = with pkgs; [
    stdenv.cc.cc.lib
    zlib.out
  ];
  python' = with pkgs; (symlinkJoin {
    name = "python";
    paths = [ python312 ];
    buildInputs = [ makeWrapper ];
    postBuild = ''
      wrapProgram "$out/bin/python3.12" --prefix LD_LIBRARY_PATH : "${lib.makeLibraryPath pythonLibs}"
    '';
  });

  packages' = with pkgs; [
    python'
    poetry
    ruff

    # Scripts
    # -- Misc
    (writeShellScriptBin "make-version" ''
      sed -i -E "s|VERSION = '([0-9.]+)'|VERSION = '\1.$(date +%y%m%d)'|g" config.py
    '')
    (writeShellScriptBin "nixpkgs-update" ''
      set -e
      hash=$(git ls-remote https://github.com/NixOS/nixpkgs nixpkgs-unstable | cut -f 1)
      sed -i -E "s|/nixpkgs/archive/[0-9a-f]{40}\.tar\.gz|/nixpkgs/archive/$hash.tar.gz|" shell.nix
      echo "Nixpkgs updated to $hash"
    '')
    (writeShellScriptBin "docker-build-push" ''
      set -e
      if command -v podman &> /dev/null; then docker() { podman "$@"; } fi
      docker push $(docker load < "$(nix-build --no-out-link)" | sed -n -E 's/Loaded image: (\S+)/\1/p')
    '')
  ];

  shell' = with pkgs; lib.optionalString isDevelopment ''
    current_python=$(readlink -e .venv/bin/python || echo "")
    current_python=''${current_python%/bin/*}
    [ "$current_python" != "${python'}" ] && rm -rf .venv/

    echo "Installing Python dependencies"
    export POETRY_VIRTUALENVS_IN_PROJECT=1
    poetry env use "${python'}/bin/python"
    poetry install --no-root --compile

    echo "Activating Python virtual environment"
    source .venv/bin/activate

    # Development environment variables
    export PYTHONNOUSERSITE=1
    export TZ=UTC

    if [ -f .env ]; then
      echo "Loading .env file"
      set -o allexport
      source .env set
      set +o allexport
    fi
  '' + lib.optionalString (!isDevelopment) ''
    make-version
  '';
in
pkgs.mkShellNoCC {
  buildInputs = pythonLibs ++ packages';
  shellHook = shell';
}
