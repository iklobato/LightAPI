# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-23.11"; # or "unstable"

  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.python3
  ];

  # Sets environment variables in the workspace
  env = {};
  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      "ms-python.python"
    ];

    # Workspace lifecycle hooks
    workspace = {
      # Runs when a workspace is first created
      onCreate = {
        create-venv = ''
          python -m venv .venv
          source .venv/bin/activate
          pip install -e .[test,docs]
        '';
      };
      # Runs when the workspace is (re)started
      onStart = {
        #activate-venv = ''
        #  echo "source .venv/bin/activate" >> ~/.bashrc
        #'';
      };
    };
  };
}
