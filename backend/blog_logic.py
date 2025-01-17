import json
from json import JSONDecodeError

from typing_extensions import Optional

from logger import setup_logger
from pathlib import Path

PostJson = list[dict[str, str]]
Post = dict[str, Optional[str | int]]
Posts = dict[Post]
Index = int


class BlogLogic:

    def __init__(self, post_file: str = "posts.json") -> None:
        """initialisation of blog class"""
        self.logger = setup_logger(__name__)
        self.logger.info("New BlogLogic instance created")
        self.POSTS_DB = Path(__file__).parent / "database" / post_file
        self.posts = self._open_persistent_storage()

    def add_post(self, new_post: Post) -> bool:
        """add new post to blogs"""
        self.logger.info(f"Starting add post routine with {new_post['title']}")
        new_id = self._get_next_index()
        if self._validate_post_contents(new_post):
            new_post["id"] = new_id
            self.posts.append(new_post)
            self._write_to_persistent_storage()
            self.logger.info("Book added to persistent storage %s", self.POSTS_DB) # noqa E501
            return True

    def delete_post(self, post_id: Index) -> Optional[Post]:
        """delete post from id"""
        self.logger.info(f"Starting delete post routine with id: {post_id}")
        found_post = self._find_post_from_id(post_id)
        if found_post:
            self.posts.remove(found_post)
            self._write_to_persistent_storage()
            self.logger.info(
                f"{found_post['title']} with id: {post_id} removed from local storage"  # noqa E501
            )
        else:
            self.logger.warning(
                f"Post with {post_id} not found in local storage"
            )  # noqa E501
            found_post = None
        return found_post

    def update_post(self, post_id: Index, edited_post: Post) -> Optional[Post]:
        """update post if valid"""
        self.logger.info(
            f"Starting update post routine with id: {post_id}: {edited_post['title']}"  # noqa E501
        )
        valid_post = self._find_post_from_id(post_id)
        valid_contents = self._validate_post_contents(edited_post)
        if valid_post and valid_contents:
            updated_post = valid_post
            updated_post["title"] = edited_post["title"]
            updated_post["content"] = edited_post["content"]
            self._write_to_persistent_storage()
            self.logger.info(f"{edited_post['title']} updated")
        else:
            updated_post = None
        return updated_post

    def queried_posts(self, search_pattern) -> Optional[Post]:
        """return post if title in storage"""
        self.logger.info(
            f"Start filter post routine with search patter: {search_pattern}"
        )
        queried_posts = list(
            filter(
                lambda post: search_pattern.lower() in post["title"].lower(),
                self.posts,  # noqa E501
            )
        )
        if queried_posts:
            found_posts = queried_posts
            self.logger.info(
                f"{len(found_posts)} post(s) found with matching search_pattern: {search_pattern}"  # noqa E501
            )
        else:
            found_posts = None
            self.logger.warning(
                f"0 posts found with matching search_pattern: {search_pattern}"
            )
        return found_posts

    def sort_posts(
        self, filtered_posts: Posts = None,
            sort: str = "title",
            direction: str = None
    ) -> Optional[Posts | None]:
        """sort posts out by criteria"""
        if not direction:
            direction = "asc"
        self.logger.info(f"Sort posts by criteria: {sort=}, {direction=}")
        posts_to_filter = filtered_posts if filtered_posts else self.posts
        direction_bool = direction.lower() != "asc"
        sort = sort.lower()
        if sort in ["content", "title"]:
            sorted_posts = sorted(
                posts_to_filter, key=lambda post: post[sort],
                reverse=direction_bool
            )
            self.logger.info(f"Posts sorted by crit: {sort=}, {direction=}")
        else:
            sorted_posts = None
            self.logger.warning("Wrong argument given to sort function, None returned") # noqa E501
        return sorted_posts

    def _get_next_index(self) -> Index:
        """get next index number"""
        return max(post["id"] for post in self.posts) + 1

    def _validate_post_contents(self, blog: Post) -> bool:
        """validate that the blog contains both elements"""
        return blog["title"] and blog["content"]

    def _open_persistent_storage(self) -> Posts | bool:
        """populate local storage from persistent storage"""
        self.logger.info("Attempting to open persistent storage")
        try:
            with open(self.POSTS_DB, "r") as read_handle:
                posts = json.load(read_handle)
                if posts:
                    self.logger.info("Persistant storage opened")
                    return posts
                else:
                    self.logger.info("Persistant storage empty")
                    return False
        except FileNotFoundError as e:
            self.logger.error(
                "File not found when opening %s %s", self.POSTS_DB, e
            )  # noqa E501
            return False
        except JSONDecodeError as e:
            self.logger.error("Error decoding JSON %s %s", self.POSTS_DB, e)
        except AttributeError as e:
            self.logger.error(
                "Error with attribute, check if file empty %s %s",
                self.POSTS_DB,
                e,  # noqa E501
            )

    def _write_to_persistent_storage(self) -> None:
        """sync local and remotre storages"""
        try:
            with open(self.POSTS_DB, "w") as write_handle:
                json.dump(self.posts, write_handle, indent=4)
                self.logger.info(
                    "Local storage written to persistent storage %s",
                    self.POSTS_DB,  # noqa E501
                )
        except FileNotFoundError as e:
            self.logger.error(
                "File not found when writing to %s %s", self.POSTS_DB, e # noqa E501

            )
    def _find_post_from_id(self, target_post_id: Index) -> Optional[Post]:
        """return post from given id"""
        self.logger.info(f"Looking up post from id:{target_post_id}")
        target_post = next(
            (post for post in self.posts if post["id"] == target_post_id), None
        )
        if target_post:
            found_post = target_post
            self.logger.info(
                f"Post found{found_post['title']} from id:{target_post_id}"
            )
        else:
            self.logger.info(f"Post not found from id:{target_post_id}")
        return found_post
