import React, { useEffect } from 'react'
import { Textarea } from "@/components/ui/textarea"
import { IoCopyOutline } from "react-icons/io5";
import { IoMdCheckmark } from "react-icons/io";
import { RxCross2, RxCheck } from "react-icons/rx";
import { FaRegEdit } from "react-icons/fa";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Form, FormControl, FormField, FormItem, FormMessage } from "@/components/ui/form"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/coordAccordion"
import { ChevronDown } from "lucide-react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"

// Schema for the text input form
const FormSchema = z.object({
    text: z.string().min(1, {
        message: "text must be at least 1 character.",
    }),
})

const FeatureCard = ({ feature, setEditDetails, searchTerm, onSegmentationComplete }) => {
    const [copied, setCopied] = React.useState(false)
    const [editing, setEditing] = React.useState(false)

    let geojsonFeature = feature.toGeoJSON();
    let type = geojsonFeature.geometry.type;
    let text = geojsonFeature.properties.text;
    let textNewLineString = text?.replace(/<br>/g, '\n');

    /************************************************************
     * Function for copy
     ************************************************************/
    useEffect(() => {
        if (copied) {
            setTimeout(() => {
                setCopied(false)
            }, 1500)
        }
    }, [copied])

    const handleCopy = () => {
        navigator.clipboard.writeText(JSON.stringify(geojsonFeature));
        setCopied(true);
    }

    const sendMinMaxToServer = async (min, max) => {
        console.log(`Sending Min and Max values to server: ${min}, ${max}`);
        try {
            const response = await fetch('http://127.0.0.1:5010/minmax', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ min, max }),
            });
            if (response.ok) {
                console.log('Min and Max values sent successfully');
                // Make sure onSegmentationComplete exists before calling
                if (onSegmentationComplete && typeof onSegmentationComplete === 'function') {
                    await onSegmentationComplete();
                }
            } else {
                console.error('Failed to send Min and Max values', response.statusText);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    };

    const CopyButton = () => {
        return (
            <Button onClick={handleCopy} variant="outline" size="icon" className={`${copied === true ? "bg-accent text-white" : ""}`}>
                <IoCopyOutline className={`h-[1.2rem] w-[1.2rem]  transition-all ${copied === true ? "-rotate-90 scale-0" : "rotate-0 scale-100"}`} />
                <IoMdCheckmark className={`absolute h-[1.2rem] w-[1.2rem] transition-all ${copied === true ? "rotate-0 scale-100" : "rotate-90 scale-0"}`} />
            </Button>
        )
    }

    const Coordinates = () => {
        const getMinMaxCoordinates = (coordinates) => {
            let minLat = Number.POSITIVE_INFINITY;
            let maxLat = Number.NEGATIVE_INFINITY;
            let minLng = Number.POSITIVE_INFINITY;
            let maxLng = Number.NEGATIVE_INFINITY;

            coordinates.forEach(line => {
                line.forEach(point => {
                    const [lng, lat] = point;
                    if (lat < minLat) minLat = lat;
                    if (lat > maxLat) maxLat = lat;
                    if (lng < minLng) minLng = lng;
                    if (lng > maxLng) maxLng = lng;
                });
            });

            return {
                min: [minLat, minLng],
                max: [maxLat, maxLng]
            };
        };

        return (
            <div className='flex flex-col gap-y-2'>
                {type === "Polygon" &&
                    // <Accordion type="single" collapsible className="w-full">
                    //     <AccordionItem value="item-1">
                    //         <div className='flex-between'>
                    //             <AccordionTrigger className='flex items-center justify-start gap-x-2'>
                    //                 📍 {geojsonFeature.geometry.coordinates[0].length} points
                    //                 <ChevronDown className="w-4 h-4 transition-transform duration-200 shrink-0" />
                    //             </AccordionTrigger>
                    //             <div className='flex justify-end col-span-1'><CopyButton /></div>
                    //         </div>

                    //         <AccordionContent>
                    //             <div className='grid w-full grid-cols-1 gap-y-2'>
                    //                 <ul className='col-span-1'>
                    //                     {geojsonFeature.geometry.coordinates.map((line, index) => (
                    //                         line.map((point, index) => (
                    //                             <li key={index} className='flex justify-between'>
                    //                                 <span className='font-bold'>{index + 1}</span>
                    //                                 <span>{point[1]}, {point[0]}</span>
                    //                             </li>
                    //                         ))
                    //                     ))}
                    //                 </ul>
                    //             </div>

                    //         </AccordionContent>
                    //     </AccordionItem>
                    // </Accordion>
                    <div className='mt-2'>
                        {(() => {
                            const { min, max } = getMinMaxCoordinates(geojsonFeature.geometry.coordinates);
                            return (
                                <div>
                                    <h1
                                    style={{
                                        fontWeight: "bold"
                                    }}
                                    >Coordinates : </h1>
                                    <p>Min: [{min[0]}, {min[1]}]</p>
                                    <p>Max: [{max[0]}, {max[1]}]</p><br />
                                    <Button onClick={() => sendMinMaxToServer(min, max)}>Start Land Detection</Button>
                                </div>
                            );
                        })()}
                    </div>
                }
            </div>
        );
    };

    /************************************************************
     * Function for text
     ************************************************************/
    const form = useForm({
        resolver: zodResolver(FormSchema),
        defaultValues: {
            text: textNewLineString || "",
        },
    })

    const onSubmitText = (data) => {
        setEditing(!editing);
        setEditDetails({ id: feature._leaflet_id, newText: data.text });
        form.reset();
    }

    // highlight text AND split text by line
    function highlightText(text, searchTerm) {
        return text.split('<br>').map((line, index) => {
            const parts = line.split(new RegExp(`(${searchTerm})`, 'gi'));
            return (
                <React.Fragment key={index}>
                    {parts.map((part, i) =>
                        part.toLowerCase() === searchTerm.toLowerCase() ? (
                            <span key={i} style={{ backgroundColor: 'yellow' }}>{part}</span>
                        ) : (
                            part
                        )
                    )}
                    {!line && <br />}
                </React.Fragment>
            );
        });
    }

    /*********************************************************************************************
     * Rendering
     *******************************************************************************************/

    return (
        <div className='py-2 flex-between gap-x-4'>
            <Card className="w-[350px]">
                <CardHeader>
                    {/* Feature # & Feauter type */}
                    <CardDescription className="pb-2 flex-between gap-x-8">
                        <>Feature #{feature._leaflet_id}</>
                        {/* {type === "Point" && <Badge className="bg-secondary">Point</Badge>}
                        {type === "LineString" && <Badge className="bg-accent">Line</Badge>}
                        {type === "Polygon" && <Badge className="bg-primary">Area</Badge>} */}
                    </CardDescription>
                    {/* Feature text */}
                    {/* <CardTitle >
                        {editing ?
                            // Edit text form 
                            <Form {...form}>
                                <form onSubmit={form.handleSubmit(onSubmitText)}  >
                                    <div className="flex items-start justify-between gap-x-4">
                                        <div className='w-full'>
                                            <FormField
                                                control={form.control}
                                                name="text"
                                                render={({ field }) => (
                                                    <FormItem>
                                                        <FormControl>
                                                            <Textarea className="min-h-[30px] w-full" placeholder="Add text" {...field} />
                                                        </FormControl>
                                                        <FormMessage />
                                                    </FormItem>
                                                )}
                                            />
                                        </div>
                                        <div className='flex-between gap-x-2'>
                                            <Button onClick={() => setEditing(false)} variant="outline" size="icon">
                                                <RxCross2 className="h-[1.2rem] w-[1.2rem]" />
                                            </Button>
                                            <Button type="submit" variant="outline" size="icon">
                                                <RxCheck className="h-[1.4rem] w-[1.4rem]" />
                                            </Button>
                                        </div>
                                    </div>
                                </form>
                            </Form>
                            :
                            // Display text
                            <div className="flex-between gap-x-4">
                                <Label htmlFor="text" className="py-1">
                                    {!text && <span className="text-gray-400">No text</span>}
                                    {text && (
                                        <div>{highlightText(text, searchTerm)}</div>
                                    )}
                                </Label>
                                <Button onClick={() => setEditing(!editing)} variant="outline" size="icon">
                                    <FaRegEdit className={`h-[1.2rem] w-[1.2rem]  transition-all ${editing === true ? "-rotate-90 scale-0" : "rotate-0 scale-100"}`} />
                                </Button>
                            </div>
                        }
                    </CardTitle> */}
                </CardHeader>
                <CardContent>
                    {/* Feature coordinates */}
                    <Coordinates />
                </CardContent>
            </Card>
        </div>
    )
}

export default FeatureCard