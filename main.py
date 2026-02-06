from hub import port, light, light_matrix, button, sound
import runloop
import app
import motor
import time
import color
import color_sensor

#LEGO SPIKE PRIME → Super safe Deposit Box
#Locks and unlocks safe both manually and through a 2-step verification 
#process that involves a color sensor, displaying a success message

# The lock motor is in port C
# The dial motor is in port B
# The dial cover motor is in port E

#EXTRA ADDITIONS-make more interesting
# The color sensor is in port D


async def success():
#actions AFTER to indicate safe has been unlocked
#change color of button to green
#makes positive noise
#displays unlocked, followed by a smiley face

    #wait 3 sec
    await runloop.sleep_ms(300)


    #positive sound
    await app.sound.play('Wand')


    #change button color to green
    light.color(light.POWER, color.GREEN)
    #light_matrix.write("unlocked")
    #await runloop.sleep_ms(600)


    #smiley face
    light_matrix.show_image(light_matrix.IMAGE_HAPPY)
    await runloop.sleep_ms(600)



# This function unlocks the safe
async def unlock():
#To check you’re in the loop
    print("UNLOCK")

    await motor.run_to_absolute_position(port.E,10,450) 
   
    start_time = time.ticks_ms()

    # timer that gives limited time to use the dial
    # starts moving closer and closer to the dial
    while motor.absolute_position(port.E) <= 500:
        await sound.beep(262,200)


        #15 degrees closer each time, until 210 reached
        await motor.run_for_degrees(port.E, 15, 5000)
        await runloop.sleep_ms(450)


        if time.ticks_diff(time.ticks_ms(), start_time) > 8000:
            await app.sound.play("Bonk")
            return
   
    # check that dial is turned enough
    while True:
        dial_pos = motor.relative_position(port.B)

        #”combination” should be more than 180
        if dial_pos >= 180:

            #automatically move dial cover all the way back since unlocked
            await motor.run_to_absolute_position(port.E, 0, 500)

            #unlock port C, lock, unlatch
            await motor.run_for_time(port.C, 1000, 500)

            #call success function
            await success()
            break

    await runloop.sleep_ms(100)



#checks if color is blue
def is_color_blue():
    return color_sensor.color(port.D) == color.BLUE


#checks if color is yellow
def is_color_yellow():
    return color_sensor.color(port.D) == color.YELLOW


#checks for unknown color
def no_color():
    app.sound.play("Car Horn")
    return color_sensor.color(port.D) == color.UNKNOWN


#criteria for Method 1 or Method 2(part 1) to call unlock/success
def unlock_condition():
    return (
        is_color_blue() or
        is_color_yellow() or
        motor.relative_position(port.C) >= 500
    )


async def main():
    # indicates that the machine is on
    await sound.beep(262, 200)
    await sound.beep(523, 200)


    # this locks the safe
    # automatically locks every time we reset the program
    await motor.run_for_time(port.C, 1000, -500)


    # reset dial
    await motor.run_to_absolute_position(port.B, 0, 500, stop=motor.COAST)
    motor.reset_relative_position(port.B, 0)


    #reset dial cover
    await motor.run_to_absolute_position(port.E, 210, 450)


    #to indicate locked deposit box
    #skull image displayed
    #button is red
    light_matrix.show_image(light_matrix.IMAGE_SKULL)
    light.color(light.POWER, color.RED)
    await runloop.sleep_ms(1000)


    # wait for unlock condition
    await runloop.until(unlock_condition or motor.relative_position(port.C)>=400)



    #method 2 = advanced-level 2 step verification
    #color/employee recognition followed by combination
    #display 13 which is a checkmark
    #calls the unlock function, for secondary verification
    if is_color_blue():
        print("Blue Detected)")
        light.color(light.POWER, color.BLUE)
        light_matrix.show_image(13)
        await unlock()


    elif is_color_yellow():
        print("Yellow Detected")
        light.color(light.POWER, color.YELLOW)
        light_matrix.show_image(13)
        await unlock()


    await runloop.sleep_ms(400)

    #method 1 = manual unlock with key
    if motor.relative_position(port.C) == -500 :
        #successful unlock, automatically calls success function
        await success()
        return


    #not blue or yellow
    await runloop.until(no_color)
    await app.sound.play('Horror Music')


runloop.run(main())