import pygame
import os

class Frontend:

  def __init__(self):
    """
    """
    os.putenv('SDL_VIDEODRIVER', 'directfb')

    # Initialize display
    pygame.display.init()

    self.size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
    self.window = pygame.display.set_mode(self.size, pygame.FULLSCREEN)
    self.screen = pygame.display.get_surface()

    # Initialize fonts
    pygame.font.init()

    self.fontHeading = pygame.font.Font('media/fonts/OpenSans-CondBold.ttf', 72)
    self.fontSubtitle = pygame.font.Font('media/fonts/OpenSans-Regular.ttf', 24)
    self.fontColor = (255, 255, 255)

    # Load background image
    self.bgImage = pygame.image.load(os.path.abspath("media/images/background.jpg"))
    self.bgImage = pygame.transform.scale(self.bgImage, self.size)

    # Load foreground images
    self.images = [
      pygame.image.load(os.path.abspath("media/images/icon-phone.png")),
      pygame.image.load(os.path.abspath("media/images/icon-youtube.png")),
      pygame.image.load(os.path.abspath("media/images/icon-warning.png")),
    ]
    self.images.append(self.images[1])

    # Initialize display state
    self.curImage = -1
    self.curTitle = ''
    self.curSubtitle = ''
    self.active = True
    self.autoUpdate = False

    # Update
    self.update()

  def setThumbImage(self, url):
    """
    Download and update thumbnail image
    """
    ret = os.system(
      'curl -o /tmp/tmpthumb.jpg \'%s\' >/dev/null 2>/dev/null' % url.replace('\'', '\\\'')
    )

    if ret == 0:
      thumbImage = pygame.image.load(os.path.abspath("/tmp/tmpthumb.jpg"))

      # Fit on 300x300 frame
      w,h = thumbImage.get_size()
      if w > h:
        h = h * 700 / w
        w = 700
      else:
        w = w * 700 / h
        h = 700

      self.images[3] = pygame.transform.scale(thumbImage, (w,h))
      self.setImage(3)

    else:
      self.setImage(1)

  def setActive(self, isActive):
    """
    """
    if self.active == isActive:
      return

    if isActive:
      pygame.display.init()
      self.size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
      self.window = pygame.display.set_mode(self.size, pygame.FULLSCREEN)
      self.screen = pygame.display.get_surface()
      self.update()

    else:
      pygame.display.quit()

    self.active = isActive

  def update(self):
    """
    """
    if not self.active:
      return

    # Draw background
    self.screen.blit(self.bgImage, (0, 0))

    # Calculate operating size
    midX = self.size[0] / 2
    imY = self.size[1] / 3
    txY = self.size[1] * 2 / 3

    # Draw image image
    if self.curImage >= 0:
      w, h = self.images[self.curImage].get_size()
      pos = (
        midX - w / 2,
        imY - h / 2
      )
      self.screen.blit(self.images[self.curImage], pos)

    # Draw title
    if self.curTitle:
      w, h = self.fontHeading.size(self.curTitle)
      pos = (
        midX - w / 2,
        txY - h / 2
      )
      self.screen.blit(
        self.fontHeading.render(self.curTitle, 0, self.fontColor),
        pos
      )

      # Draw subtitle
      if self.curSubtitle:
        ws, hs = self.fontSubtitle.size(self.curSubtitle)
        pos = (
          midX - ws / 2,
          pos[1] + h + 10
        )
        self.screen.blit(
          self.fontSubtitle.render(self.curSubtitle, 0, self.fontColor),
          pos
        )

    # Update image
    pygame.display.update()

  def setTitle(self, title):
    """
    """
    self.curTitle = title
    if self.autoUpdate:
      self.update()

  def setSubTitle(self, title):
    """
    """
    self.curSubtitle = title
    if self.autoUpdate:
      self.update()

  def setImage(self, image):
    """
    """
    self.curImage = image
    if self.autoUpdate:
      self.update()
