"""
Contains the tick, main, and level_editor functions.
"""

from math import sqrt
import json
import pygame
from vector import Vector
from controller import Controller, LEController
from level import Level, LELevel
from view import View, LEView


def tick(dt, max_angular_velocity, jump_sound, level, controller, view):
    """
    Step the simulation forward one timestep.

    Args:
        dt: A float, the length of the timestep.
        max_angular_velocity: An integer or float, the maximum angular velocity
        the player can have and and still use the controller to make themself
        faster in the direction they are spinning
        jump_sound: A string, the path to an audio file to be played
        when the player presses the jump button.
        level: A Level, the level to update.
        controller: A Controller, the controller to take player inputs from.
        view: A View, the view to display the level to.
    """
    # Apply the effects of the roll control from the player.
    roll_torque, roll_force = controller.roll
    if (
        roll_torque * level.player.angular_velocity < 0
        or abs(level.player.angular_velocity) < max_angular_velocity
    ):
        level.player.angular_accelerate(roll_torque, dt)
    if (
        roll_force * level.player.velocity.x < 0
        or abs(level.player.velocity.x) <
        max_angular_velocity * level.player.radius
    ):
        level.player.accelerate(Vector(roll_force, 0), dt)

    # Play the jump sound if the player has just pressed the jump key.
    if controller.play_jump:
        view.play_sound_effect(jump_sound)

    # Update the level.
    level.update(dt)
    level.apply_collisions(
        controller.is_jumping, controller.is_bouncing
    )
    position_change = level.update_portals(dt)
    if position_change is not None:
        view.move_camera(position_change)
    if controller.restart:
        level.restart()

    # Update the camera position based on the player's position.
    view.update_lerp(dt)


def main():
    """
    Run the physics simulator, take player input,
    and display the state of the game to a window.
    """
    # Set all constants.
    # --------------------------------------------------------------------------
    fps = 40
    mode = "normal"
    portals = "close"
    starting_level = "level_1"
    # --------------------------------------------------------------------------
    dt = 1 / fps
    with open(f"constants/{mode}_mode.json", "r", encoding="utf-8") as file:
        constants = json.load(file)
    max_angular_velocity = constants["max_angular_velocity"]
    jump_sound = constants["jump_sound"]

    # Initialize the level, controller, view, and clock.
    with open(f"portal_configs/{portals}.json", "r", encoding="utf-8") as file:
        portals = json.load(file)
    level = Level(f"{starting_level}/", portals, constants)
    controller = Controller(constants)
    view = View(level, "sprites/", constants)
    clock = pygame.time.Clock()

    # Run the game until the window is closed.
    while True:
        # If the window is closed, quit the game.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                print(f"final position = {level.player.position}")
                exit()

        # Update the controller.
        controller.update(dt)

        # Tick the Level forward in time.
        tick(
            dt, max_angular_velocity, jump_sound, level, controller, view
        )

        # Draw the current state of the level to the window.
        view.refresh()
        pygame.display.update()
        clock.tick(fps)


def level_editor():
    """
    Run the physics simulator, take player input, take level editor input,
    and display the state of the game to a window.
    """
    # Set all constants.
    # --------------------------------------------------------------------------
    fps = 40
    mode = "normal"
    portals = "close"
    starting_level = "ella_1"
    click_distance = 10
    snap_distance = 25
    # --------------------------------------------------------------------------
    dt = 1 / fps
    with open(f"constants/{mode}_mode.json", "r", encoding="utf-8") as file:
        constants = json.load(file)
    max_angular_velocity = constants["max_angular_velocity"]
    jump_sound = constants["jump_sound"]

    # Initialize the level, controller, view, and clock.
    with open(f"portal_configs/{portals}.json", "r", encoding="utf-8") as file:
        portals = json.load(file)
    level = LELevel(f"{starting_level}/", portals, constants)
    controller = LEController(constants)
    view = LEView(level, "sprites/", constants)
    clock = pygame.time.Clock()
    editing_index = None
    dragging_player = False
    last_player_position = None

    # Run the game until the window is closed.
    while True:
        # If the window is closed, quit the game.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                print(f"final position = {level.player.position}")
                level.finish_editing()
                exit()

        # Update the controller.
        controller.update(dt)

        # If the game is paused, enter level editor mode.
        if controller.is_paused:
            # Calculate the position of the editor in world space.
            editor_position = controller.editor_position
            if editor_position is not None:
                editor_position = Vector.diff(
                    view.camera, editor_position)

            # Update the camera position based on mouse dragging.
            camera_displacement = controller.camera_drag_displacement
            view.move_camera(camera_displacement)

            # If the editor is toggling dynamic, toggle dynamic.
            if controller.toggle_dynamic:
                level.toggle_dynamic()

            # If the editor is toggling bouncy, toggle bouncy.
            if controller.toggle_bouncy:
                level.toggle_bouncy()

            # If the editor presses delete, delete the editing vertex or shape.
            if controller.delete:
                if(level.editing_polygon is not None and
                    editing_index is not None):
                    level.remove_editing_vertex(editing_index)
                    editing_index = None
                else:
                    level.delete_editing_shape()

            # If the editor presses enter, finish editing the shape.
            if controller.finish_editing:
                level.finish_editing()

            # If the editor is dragging the player:
            if dragging_player:
                if editor_position is not None:
                    level.drag_player(
                        Vector.diff(
                            last_player_position,
                            editor_position
                        )
                    )
                    last_player_position = level.player.position
                else:
                    dragging_player = False

            # If the editor is editing a circle.
            if level.editing_circle is not None:
                if controller.edit_click:
                    # If the editor clicks on the circle's circumference:
                    if abs(sqrt(Vector.diff(
                        editor_position,
                        level.editing_circle[0]
                        ).magnitude_squared()) - (
                        level.editing_circle[1])
                    ) < click_distance:
                        # Edit its radius.
                        editing_index = 1

                    # If the editor clicks on the circle's center:
                    elif Vector.diff(
                        editor_position,
                        level.editing_circle[0]
                    ).magnitude_squared() < click_distance * click_distance:
                        # Edit its position
                        editing_index = 0

                # If the editor is not holding edit,
                # they aren't editing anything.
                elif editor_position is None:
                    editing_index = None

                # If the editor is editing the circle's radius:
                elif editing_index == 1:
                    # Find the distance between the circle's center
                    # and the editing position.
                    distance = sqrt(Vector.diff(
                        editor_position,
                        level.editing_circle[0]
                    ).magnitude_squared())
                    # Round up that distance to the nearest multiple
                    # of the snap distance and set the circle's radius to that.
                    level.set_editing_circle_radius(
                        (distance // snap_distance + 1) * snap_distance
                    )

                # If the editor is editing the circle's position:
                if editing_index == 0:
                    # Snap the editor's position
                    # to the nearest point on the grid.
                    new_position = editor_position.snap_grid(snap_distance)

                    # Set that as the circle's position.
                    level.set_editing_circle_position(new_position)

            # If the editor is editing a polygon:
            elif level.editing_polygon is not None:
                # If the editor clicks on one of the polygon's vertices:
                if controller.edit_click:
                    for v, vertex in enumerate(level.editing_polygon):
                        if Vector.diff(
                        editor_position,
                        vertex
                    ).magnitude_squared() < click_distance * click_distance:
                            # Start moving that vertex.
                            editing_index = v
                            break

                    # If the editor is not editing a vertex,
                    # start editing a new vertex.
                    if editing_index is None:
                        # Find between which two vertices
                        # the new vertex should be.
                        closest_edge = None
                        closest_vertex = None
                        shortest_distance = None
                        # For each index:
                        for v, vertex in enumerate(level.editing_polygon):
                            # Find the distance to the edge:
                            distance = editor_position.edge_point_distance(
                                vertex,
                                level.editing_polygon[v - 1]
                            )

                            # If that is the shortest distance so far,
                            # record it.
                            if distance is not None:
                                distance = abs(distance)
                                if shortest_distance is None or (
                                distance < shortest_distance
                                ):
                                    shortest_distance = distance
                                    closest_edge = v
                                    closest_vertex = None

                            # Find the distance to the vertex.
                            distance = sqrt(Vector.diff(
                                editor_position, vertex
                            ).magnitude_squared())

                            # If that is the shortest distance so far,
                            # record it.
                            if shortest_distance is None or (
                            distance < shortest_distance
                            ):
                                shortest_distance = distance
                                closest_edge = None
                                closest_vertex = v

                        # If the closest point on the polygon's
                        # border is on a vertex,
                        # find which edge is closest.
                        if closest_edge is None:
                            direction = Vector.sum(
                                Vector.diff(
                                    vertex,
                                    level.editing_polygon[v - 1]
                                ).normal(),
                                Vector.diff(
                                    vertex,
                                    level.editing_polygon[(v + 1) %
                                        len(level.editing_polygon)]
                                ).normal()
                            )
                            side = editor_position.edge_point_distance(
                                vertex, direction, False
                            )
                            if side < 0:
                                closest_edge = closest_vertex
                            else:
                                closest_edge = closest_vertex - 1

                        # Add and start editing the new vertex.
                        level.add_editing_vertex(
                            editor_position.snap_grid(snap_distance),
                            closest_edge
                        )
                        editing_index = closest_edge

                # If the editor is not holding edit,
                # they aren't editing anything.
                elif editor_position is None:
                    editing_index = None

                # If the editor is editing a vertex:
                if editing_index is not None:
                    # Snap the editor's position
                    # to the nearest point on the grid.
                    new_position = editor_position.snap_grid(snap_distance)

                    # Set that as the vertex's position.
                    level.move_editing_vertex(editing_index, new_position)

            # If the editor is not editing anything:
            else:
                # If the editor opens a new circle:
                if controller.new_circle and controller.edit_click:
                    # Make a new editing circle and start editing the radius.
                    level.new_editing_circle(
                        editor_position.snap_grid(snap_distance),
                        snap_distance
                    )
                    editing_index = 1
                    continue

                # If the editor opens a new polygon:
                if controller.new_polygon and controller.edit_click:
                    # Make a new editing polygon
                    # and start editing the first vertex.
                    level.new_editing_polygon(
                        editor_position.snap_grid(snap_distance)
                    )
                    editing_index = 0
                    continue

                # If the editor clicks on the player:
                if controller.edit_click and Vector.diff(
                    editor_position,
                    level.player.position
                ).magnitude_squared() < (
                level.player.radius * level.player.radius):
                    # Start dragging the player
                    dragging_player = True
                    last_player_position = level.player.position
                    continue

                # If the editor clicks on a pre-existing circle:
                if controller.edit_click:
                    for c, circle in enumerate(level.circles):
                        if Vector.diff(
                            editor_position,
                            circle.position
                        ).magnitude_squared() < circle.radius * circle.radius:
                            # Start editing that circle
                            level.edit_existing_circle(c)
                            editing_index = None
                            continue
                    for c, circle in enumerate(level.dynamic_circles):
                        if Vector.diff(
                            editor_position,
                            circle.position
                        ).magnitude_squared() < circle.radius * circle.radius:
                            # Start editing that circle
                            level.edit_existing_dynamic_circle(c)
                            editing_index = None
                            continue

                    # If the clicks on a pre-existing polygon:
                    for p, polygon in enumerate(level.polygons):
                        if editor_position.is_in_polygon(
                            polygon.world_vertices):
                            # Start editing that polygon.
                            level.edit_existing_polygon(p)
                            editing_index = None
                            continue
                    for p, polygon in enumerate(level.dynamic_polygons):
                        if editor_position.is_in_polygon(
                            polygon.world_vertices):
                            # Start editing that polygon.
                            level.edit_existing_dynamic_polygon(p)
                            editing_index = None
                            continue

        # Otherwise, tick the Level forward in time.
        else:
            tick(
                dt,
                max_angular_velocity,
                jump_sound,
                level,
                controller,
                view
            )

        # Draw the current state of the level to the window.
        view.refresh()
        pygame.display.update()
        clock.tick(fps)

if __name__ == "__main__":
    level_editor()
