"""
A manager for repository repositories.

This class allows to maintain a local stash of repository repositories that
can consistently be accessed without loading any repository multiple
times.
"""

from os import listdir, rmdir
from tempfile import mkdtemp
from typing import Final

from latexgit.repository.git import GitRepository
from latexgit.utils.path import Path
from latexgit.utils.strings import enforce_url
from latexgit.utils.types import type_error


class GitManager:
    """A git repository manager can provide a set of git repositories."""

    def __init__(self, base_dir: str) -> None:
        """
        Set up the git repository manager.

        :param base_dir: the base directory
        """
        #: the base directory of the repository manager
        self.base_dir: Final[Path] = Path.path(base_dir)
        self.base_dir.ensure_dir_exists()
        #: the internal set of github repositories
        self.__repos: Final[dict[str, GitRepository]] = {}

        #: load all the repository repositories
        for thedir in listdir(self.base_dir):
            fullpath = self.base_dir.resolve_inside(thedir)
            if fullpath.is_dir() and fullpath.resolve_inside(".git").is_dir():
                gr: GitRepository = GitRepository.from_local(fullpath)
                self.__repos[gr.url] = gr

    def get_repo(self, url: str) -> GitRepository:
        """
        Get the git repository for the given URL.

        :param url: the URL to load
        :return: the repository
        """
        url = enforce_url(url)
        if url in self.__repos:
            return self.__repos[url]

        dirpath: Final[Path] = Path.directory(mkdtemp(
            dir=self.base_dir, prefix="git_"))
        try:
            gt: Final[GitRepository] = GitRepository.download(url, dirpath)
        except ValueError:
            rmdir(dirpath)
            raise
        self.__repos[gt.url] = gt
        self.__repos[url] = gt
        return gt

    def get_file(self, repo_url: str, relative_path: str) -> Path:
        """
        Get a path to a file from the given git repository.

        :param repo_url: the repository url.
        :param relative_path: the relative path
        :return: the file
        """
        if not isinstance(relative_path, str):
            raise type_error(relative_path, "relative_path", str)
        file: Final[Path] = self.get_repo(repo_url).path.resolve_inside(
            relative_path)
        file.enforce_file()
        return file
