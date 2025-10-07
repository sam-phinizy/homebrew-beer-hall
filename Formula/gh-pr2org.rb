class GhPr2org < Formula
  desc "Sync GitHub PRs where you're tagged into an Emacs org-mode file"
  homepage "https://github.com/sam-phinizy/homebrew-beer-hall"
  version "1.0.0"
  url "https://github.com/sam-phinizy/homebrew-beer-hall/releases/download/gh-pr2org/v#{version}/gh-pr2org.py"
  sha256 "d2026bb663f53e9cee6c85030dc11586a21a21694fb652131a028b7cd0eaf803"
  license "MIT"

  depends_on "gh"
  depends_on "python@3.12"
  depends_on "uv"

  def install
    libexec.install "gh-pr2org.py"

    (bin/"gh-pr2org").write <<~EOS
      #!/bin/bash
      exec uv run "#{libexec}/gh-pr2org.py" "$@"
    EOS
  end

  test do
    assert_match "usage", shell_output("#{bin}/gh-pr2org --help 2>&1", 2)
  end
end
