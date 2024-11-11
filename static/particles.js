// Initialize tsParticles
tsParticles.load("particles-js", {
    fpsLimit: 60,
    backgroundMode: {
        enable: true,
        zIndex: -1
    },
    particles: {
        number: {
            value: 0, // Start with zero particles
            density: {
                enable: false,
                area: 800
            }
        },
        color: {
            value: [
                "#3998D0",
                "#2EB6AF",
                "#A9BD33",
                "#FEC73B",
                "#F89930",
                "#F45623",
                "#D62E32",
                "#EB586E",
                "#9952CF"
            ]
        },
        life: {
            duration: {
                sync: false,
                value: 5 // Adjust duration as needed
            },
            count: 1
        },
        shape: {
            type: "circle"
        },
        size: {
            value: 15,
            random: {
                enable: true,
                minimumValue: 10
            }
        },
        move: {
            enable: true,
            speed: 2,
            outModes: {
                default: "destroy"
            }
        },
        destroy: {
            mode: "split",
            split: {
                count: 1,
                factor: {
                    value: 3,
                    random: {
                        enable: true,
                        minimumValue: 2
                    }
                },
                rate: {
                    value: {
                        min: 2,
                        max: 4
                    }
                },
                particles: {
                    life: {
                        count: 1,
                        duration: {
                            value: 3
                        }
                    },
                    move: {
                        speed: 2,
                        outModes: {
                            default: "destroy"
                        }
                    }
                }
            }
        }
    },
    emitters: {
        direction: "none",
        rate: {
            delay: 1, // Emit particles every second
            quantity: 5 // Number of particles emitted each time
        },
        size: {
            width: 100,
            height: 100
        },
        position: {
            x: 50,
            y: 50
        }
    },
    interactivity: {
        detectsOn: "canvas",
        events: {
            onHover: {
                enable: false
            },
            onClick: {
                enable: false
            },
            resize: true
        }
    },
    detectRetina: true
});
