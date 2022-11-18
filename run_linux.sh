#!/usr/bin/env bash
set -eu
if [[ $OSTYPE != linux* ]]; then
    echo "Skipping install script - not on Linux"
    exit
fi
if command -v sudo &>/dev/null && command -v apt &>/dev/null; then
    APT_CMD="sudo apt"
elif command -v apt &>/dev/null; then
    APT_CMD=apt
fi
if [[ $APT_CMD != "" ]]; then
    if ! command -v chronic &>/dev/null; then
        $APT_CMD -qq install -y moreutils
    fi
    echo "Installing packages, please wait..."
    chronic $APT_CMD install -y \
        build-essential \
        curl \
        git \
        htop \
        libbz2-dev \
        libffi-dev \
        liblzma-dev \
        libncursesw5-dev \
        libreadline-dev \
        libsqlite3-dev \
        libssl-dev \
        libxml2-dev \
        libxmlsec1-dev \
        llvm \
        make \
        moreutils \
        neovim \
        sqlite3 \
        tmux \
        wget \
        xz-utils \
        zlib1g-dev \
        zsh
fi
if [[ ! -f ~/.local/share/nvim/site/autoload/plug.vim ]]; then
    curl -sfLo ~/.local/share/nvim/site/autoload/plug.vim --create-dirs \
        https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
fi
mkdir -p ~/.vim/autoload
cp -t ~/.vim/autoload ~/.local/share/nvim/site/autoload/plug.vim
if [[ ! -d ~/.config/nvim/pack/gpanders/start/editorconfig.nvim ]]; then
    git clone https://github.com/gpanders/editorconfig.nvim ~/.config/nvim/pack/gpanders/start/editorconfig.nvim
else
    git -C ~/.config/nvim/pack/gpanders/start/editorconfig.nvim pull
fi
ln -sf ~/.vimrc ~/.config/nvim/init.vim
