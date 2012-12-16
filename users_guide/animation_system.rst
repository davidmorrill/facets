.. _animation_system:

The Animation System
====================

As described earlier, the Facets *animation system* provides a program
controlled means of changing object attributes over time. In this section we'll
provide a more in depth look at the various parts of the animation system, which
can be divided into the following topics:

Animation objects
  The animation system defines a number of animation classes that do all of the
  actual work needed to animate facet values over time. These classes are at the
  core of the animation system and perform such tasks as:

  * Animating a single object facet over time.
  * Coordinating the concurrent execution of a collection of animations.
  * Coordinating the sequential execution of a collection of animations that
    should run one right after the other.

Path objects
  An animation consists of modifying the value of an object facet over time,
  starting with an initial *begin* value and ending at a final *end* value. The
  entire set of values that are sequentially assignable to an object facet
  during an animation cycle is referred to as the animation's *path*. The
  animation system provides a number of path classes that compute the set of
  path values given the animation's *begin* value, *end* value and *current
  time*.

  There is more than one path class because there are many ways to produce a set
  of intermediate values from any given pair of *begin* and *end* values. In
  most cases, how the intermediate values are calculated depends upon the type
  of the begin and end values. A path for a pair of floating point values is
  probably very different than the path for a pair of strings.

  The animation system provides a useful collections of path classes that handle
  many of the most common animatable value types, such as:

  * int
  * float
  * (int, int) tuple (e.g. a 2D point on an integer grid)
  * (float, float) tuple (e.g. a 2D point on a continuous grid)
  * str

  You can also create your own custom path classes to handle additional data
  types and algorithms for computing intermediate values.

Tweener objects
  As just described, a path defines the set of intermediate values that can be
  assigned to an animated facet as it traverses from its *begin* to *end*
  values. A *tweener* object, on the other hand, manages the flow of time during
  a facet's animation.

  Think of a movie. A movie consists of a series of individual stills, or
  frames, which are shown rapidly and sequentially to achieve the effect of
  continuous motion. Using our animation terminology, we can think of the
  collection of individual still images as forming our animation *path*. We
  start by showing the first still image, then the second, and so on until we
  have shown the last image, at which point the animation is complete.

  Now think of some of the common *special effects* such as *slow mo'* and *fast
  forward* we are so used to seeing when watching a movie. In essence, these
  special effects are actually affecting the flow of time as we sequence through
  the individual images forming the movie. A slow motion effect reduces the rate
  of flow of time for a certain period, making the length of time each
  individual image is shown longer than it would normally be (metaphorically
  speaking, since the technical details of doing this are actually quite
  different). It's still the same set of images (or *path* values) being shown,
  but at a different rate of flow of time, since some images are shown for
  longer periods of time than others.

  In essence, tweener objects allow us to add time-related *special effects* to
  an animation by varying the rate of flow of time from the beginning of the
  animation to the end of the animation. The same set of path values are still
  being used, but the rate at which the animation moves from one value to the
  next can vary over time.

  Now, an astute reader might wonder why a path object couldn't perform the job
  of a tweener as well, handling both the task of computing the intermediate
  values and managing the time at which they are used. And the answer is, of
  course, that it could, but the resulting system would not be as flexible or
  easy to use.

  Consider our movie example again. Image a scene where the protagonist is
  jumping onto the roof of a moving train. For dramatic purposes we want to show
  the jump and landing in slow motion. Now we could try to film the sequence in
  slow motion by creating a system where the actor or stunt man is in some kind
  of a motion control harness that moves him or her very slowly onto the roof of
  a barely crawling train. This might work, but the results would probably be
  very unsatisafactory and expensive to produce. The more likely scenario is
  that the stunt man just jumps onto the moving train with cameras rolling and
  they add the slow motion effect in post. Much simpler and more cost effective.

  By separating the path from the rate of flow of time, we simplify the process
  of creating paths and open up more possibilities for creatively using them in
  animations through the application of different types of tweeners.

  The animation system includes a number of the most common types of tweeners:

  Linear
    Just uses the path values as they are, without affecting the flow of time.

  Ease out
    Starts out slow, then speeds up at the end.

  Ease in
    Start out fast, then slows down at the end.

  Ease out, Ease in
    Starts out slow, speeds up, then slows down again at the end.

  You can of course create your own tweener classes to handle any custom
  animation requirements you might have.

HasFacets animation methods
  Although Facets animation can be performed using just animation, path and
  tweener objects, the core **HasFacets** class defines a small set of helper
  methods that make it easier to create and manage animations for attributes on
  any Facets-based object. The helper methods allow you to:

  * Create and run an animation on an object facet.
  * Find all currently running animations on one or more object facets.
  * Halt execution of all currently running animations on one or more object
    facets.

With these introductory descriptions in mind, you can either continue on and
read through all of the animation topics in order, or jump to a section of
particular interest using the following links:

.. toctree::
   :maxdepth: 1

   animation_objects
   animation_path_objects
   animation_tweener_objects
   animation_methods
