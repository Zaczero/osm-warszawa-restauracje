{ pkgs ? import <nixpkgs> { }, ... }:

let
  shell = import ./shell.nix {
    isDevelopment = false;
  };

  python-venv = pkgs.buildEnv {
    name = "python-venv";
    paths = [
      (pkgs.runCommand "python-venv" { } ''
        mkdir -p $out/lib
        cp -r "${./.venv/lib/python3.12/site-packages}"/* $out/lib
      '')
    ];
  };
in
with pkgs; dockerTools.buildLayeredImage {
  name = "docker.monicz.dev/osm-warszawa-restauracje";
  tag = "latest";
  maxLayers = 10;

  contents = shell.buildInputs ++ [ python-venv ];

  extraCommands = ''
    set -e
    mkdir app && cd app
    mkdir cache data
    cp "${./.}"/*.py .
    export PATH="${lib.makeBinPath shell.buildInputs}:$PATH"
    ${shell.shellHook}
  '';

  config = {
    WorkingDir = "/app";
    Volumes = {
      "/app/cache" = { };
      "/app/data" = { };
    };
    Env = [
      "PYTHONPATH=${python-venv}/lib"
      "PYTHONUNBUFFERED=1"
      "PYTHONDONTWRITEBYTECODE=1"
    ];
    Entrypoint = [ "python" "main.py" ];
    Cmd = [ ];
  };
}
