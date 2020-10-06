import QtQuick 2.9
import QtQuick.Window 2.2



Window {
    visible: true
    width: 240
    height: 240
    x: 0
    y: 0
    flags: Qt.FramelessWindowHint

    property string svgRobotAPath: "file:///home/pi/svgQmlTest/svg/robot-a/"
    property string svgRobotBPath: "file:///home/pi/svgQmlTest/svg/robot-b/"
    property string animationRobotAPath: "file:///home/pi/svgQmlTest/gif/robot-a/"
    property string animationRobotBPath: "file:///home/pi/svgQmlTest/gif/robot-b/"

    Rectangle{
        anchors.fill: parent
        focus: true

        Keys.onPressed: {
            if(event.key === Qt.Key_0)
                face.source = animationRobotAPath + "neutral-afraid.gif"
            else if(event.key === Qt.Key_1)
                face.source = animationRobotAPath + "neutral-angry.gif"
            else if(event.key === Qt.Key_3)
                face.source = animationRobotAPath + "neutral-blink.gif"
            else if(event.key === Qt.Key_4)
                face.source = animationRobotAPath + "neutral-happy.gif"
            else if(event.key === Qt.Key_5)
                face.source = animationRobotAPath + "neutral-sad.gif"
            else if(event.key === Qt.Key_6)
                face.source = animationRobotAPath + "neutral-smile.gif"
            else if(event.key === Qt.Key_7)
                face.source = animationRobotAPath + "neutral-surprise.gif"
            else if(event.key === Qt.Key_8)
                face.source = animationRobotAPath + "neutral-talk.gif"
            else if(event.key === Qt.Key_9)
                face.source = animationRobotBPath + "afraid.gif"
            else if(event.key === Qt.Key_A)
                face.source = animationRobotBPath + "angry.gif"
            else if(event.key === Qt.Key_B)
                face.source = animationRobotBPath + "blink.gif"
            else if(event.key === Qt.Key_C)
                face.source = animationRobotBPath + "happy.gif"
            else if(event.key === Qt.Key_D)
                face.source = animationRobotBPath + "sad.gif"
            else if(event.key === Qt.Key_E)
                face.source = animationRobotBPath + "smile.gif"
            else if(event.key === Qt.Key_F)
                face.source = animationRobotBPath + "surprized.gif"
            else if(event.key === Qt.Key_G)
                face.source = animationRobotBPath + "talk.gif"
            else if(event.key === Qt.Key_Down){
                face.visible = false
                pic.visible = true
            }
            else if(event.key === Qt.Key_Up){
                face.visible = true
                pic.visible = false
            }
            else if(event.key === Qt.Key_H)
                pic.source = svgRobotAPath + "afraid.svg"
            else if(event.key === Qt.Key_I)
                pic.source = svgRobotAPath + "angry.svg"
            else if(event.key === Qt.Key_J)
                pic.source = svgRobotAPath + "blink.svg"
            else if(event.key === Qt.Key_K)
                pic.source = svgRobotAPath + "happy.svg"
            else if(event.key === Qt.Key_L)
                pic.source = svgRobotAPath + "sad.svg"
            else if(event.key === Qt.Key_M)
                pic.source = svgRobotAPath + "smile.svg"
            else if(event.key === Qt.Key_N)
                pic.source = svgRobotAPath + "surprise.svg"
            else if(event.key === Qt.Key_O)
                pic.source = svgRobotBPath + "neutral.svg"
            else if(event.key === Qt.Key_P)
                pic.source = svgRobotBPath + "afraid.svg"
            else if(event.key === Qt.Key_Q)
                pic.source = svgRobotBPath + "angry.svg"
            else if(event.key === Qt.Key_R)
                pic.source = svgRobotBPath + "blink.svg"
            else if(event.key === Qt.Key_S)
                pic.source = svgRobotBPath + "happy.svg"
            else if(event.key === Qt.Key_T)
                pic.source = svgRobotBPath + "sad.svg"
            else if(event.key === Qt.Key_U)
                pic.source = svgRobotBPath + "smile.svg"
            else if(event.key === Qt.Key_V)
                pic.source = svgRobotBPath + "surprise.svg"
            else if(event.key === Qt.Key_W)
                pic.source = svgRobotBPath + "neutral.svg"

        }

        AnimatedImage{
            id: face
            visible: true
            anchors.centerIn: parent
            source: animationRobotAPath + "neutral-afraid.gif"
            fillMode: Image.PreserveAspectCrop
            focus: false
        }

        Image{
            id: pic
            visible: false
            anchors.centerIn: parent
            source: svgRobotAPath + "afraid.svg"
            focus: false
        }

    }





//    Timer{
//        interval: 500
//        running: false
//        repeat: true
//        onTriggered: face.state = "state1"
//    }

}
