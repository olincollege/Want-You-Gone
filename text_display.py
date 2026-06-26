"""
Contains the TextDisplay class.
"""

import pygame


class TextDisplay:
    """
    Displays fading title/caption text on screen, in the style of the
    chapter title cards in Portal 2.

    A caption goes through three phases, driven by a single timer:
      - fade in: alpha rises from 0 to 255 over _FADE_IN seconds.
      - hold: alpha stays at 255 for _HOLD seconds.
      - fade out: alpha falls from 255 to 0 over _FADE_OUT seconds.

    Call show() to start a caption, update() once per frame to advance
    the timer, and draw() once per frame to blit it to the window.

    Attributes:
        _FADE_IN: A float representing the fade in duration in seconds.
        _HOLD: A float representing the hold duration in seconds.
        _FADE_OUT: A float representing the fade out duration in seconds.
        _COLOR: A tuple representing the RGB color to draw the text.
        _TITLE_FONT: A Font used to render the main line of text.
        _SUBTITLE_FONT: A Font used to render the secondary line of text.
        _timer: A float representing the seconds since the current
        caption started.
        _title_surface: A Surface with the rendered title text, cached so
        it isn't re-rendered every frame. None if no caption is active.
        _subtitle_surface: A Surface with the rendered subtitle text,
        or None if there is no subtitle (or no active caption).
    """

    def __init__(self, constants):
        """
        Initialize all timing, color, and font attributes.

        Args:
            constants: A dictionary representing all the constants,
            expected to contain "caption_fade_in", "caption_hold",
            "caption_fade_out", "caption_color", "caption_font_path",
            "caption_title_size", and "caption_subtitle_size".
        """
        self._FADE_IN = constants["caption_fade_in"]
        self._HOLD = constants["caption_hold"]
        self._FADE_OUT = constants["caption_fade_out"]
        self._COLOR = tuple(constants["caption_color"])

        # A font path of None falls back to pygame's default font.
        font_path = constants.get("caption_font_path") or None
        self._TITLE_FONT = pygame.font.Font(
            font_path, constants["caption_title_size"]
        )
        self._SUBTITLE_FONT = pygame.font.Font(
            font_path, constants["caption_subtitle_size"]
        )

        # Start with no caption active (timer already past fade out).
        self._timer = self._FADE_IN + self._HOLD + self._FADE_OUT
        self._title_surface = None
        self._subtitle_surface = None

    def show(self, title, subtitle=None):
        """
        Start displaying a new caption from the beginning of its fade in.

        Renders the text to cached surfaces once, so draw() can cheaply
        re-blit the same surfaces every frame at the current alpha.

        Args:
            title: A string representing the main line of text to display.
            subtitle: A string representing the smaller line of text to
            display below the title. None for no subtitle.
        """
        self._timer = 0
        self._title_surface = self._TITLE_FONT.render(
            title, True, self._COLOR
        )
        self._subtitle_surface = (
            self._SUBTITLE_FONT.render(subtitle, True, self._COLOR)
            if subtitle is not None
            else None
        )

    def update(self, dt):
        """
        Advance the caption timer by one frame.

        Call this once per frame, regardless of whether a caption is
        currently active.

        Args:
            dt: A float representing the frame duration in seconds.
        """
        self._timer += dt

    @property
    def is_active(self):
        """
        True while a caption is fading in, holding, or fading out.

        Returns:
            A boolean.
        """
        total_duration = self._FADE_IN + self._HOLD + self._FADE_OUT
        return self._title_surface is not None and self._timer < total_duration

    @property
    def _alpha(self):
        """
        The current opacity of the caption.

        Returns:
            An int between 0 and 255 representing how opaque the caption
            text should currently be drawn, based on which phase
            (fade in, hold, fade out) the timer is in.
        """
        if self._timer < self._FADE_IN:
            return int(255 * (self._timer / self._FADE_IN))
        if self._timer < self._FADE_IN + self._HOLD:
            return 255
        fade_out_timer = self._timer - self._FADE_IN - self._HOLD
        if fade_out_timer < self._FADE_OUT:
            return int(255 * (1 - fade_out_timer / self._FADE_OUT))
        return 0

    def draw(self, window):
        """
        Draw the current caption onto a window at the current alpha.

        Drawn directly in screen space (no camera offset), so it sits
        as a fixed overlay regardless of where the player is in the
        level. Does nothing if no caption is active.

        Args:
            window: A Surface representing the window to draw onto.
        """
        if not self.is_active:
            return

        alpha = self._alpha
        center_x = window.get_width() // 2
        baseline_y = window.get_height() - 140

        self._title_surface.set_alpha(alpha)
        title_rect = self._title_surface.get_rect(
            center=(center_x, baseline_y)
        )
        window.blit(self._title_surface, title_rect)

        if self._subtitle_surface is not None:
            self._subtitle_surface.set_alpha(alpha)
            subtitle_rect = self._subtitle_surface.get_rect(
                center=(center_x, baseline_y + 40)
            )
            window.blit(self._subtitle_surface, subtitle_rect)
