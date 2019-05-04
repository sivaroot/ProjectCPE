import vtk
def setVtkWidget(vtkWidget):

        colors = vtk.vtkNamedColors()

        # Create the RenderWindow, Renderer and Interactor.
        #

        ren1 = vtk.vtkRenderer()
        vtkWidget.GetRenderWindow().AddRenderer(ren1)



        iren = vtkWidget.GetRenderWindow().GetInteractor()

        reader = vtk.vtkMetaImageReader()
        reader.SetFileName('FullHead.mha')
        reader.Update()

        locator = vtk.vtkMergePoints()
        locator.SetDivisions(396, 396, 24)
        locator.SetNumberOfPointsPerBucket(1)
        locator.AutomaticOff()

        iso = vtk.vtkMarchingCubes()
        iso.SetInputConnection(reader.GetOutputPort())
        iso.ComputeGradientsOn()
        iso.ComputeScalarsOff()
        iso.SetValue(0, 1)
        iso.SetLocator(locator)

        isoMapper = vtk.vtkPolyDataMapper()
        isoMapper.SetInputConnection(iso.GetOutputPort())
        isoMapper.ScalarVisibilityOff()

        isoActor = vtk.vtkActor()
        isoActor.SetMapper(isoMapper)
        isoActor.GetProperty().SetColor(colors.GetColor3d("Wheat"))

        outline = vtk.vtkOutlineFilter()
        outline.SetInputConnection(reader.GetOutputPort())

        outlineMapper = vtk.vtkPolyDataMapper()
        outlineMapper.SetInputConnection(outline.GetOutputPort())

        outlineActor = vtk.vtkActor()
        outlineActor.SetMapper(outlineMapper)

        # Add the actors to the renderer, set the background and size.
        #
        ren1.AddActor(outlineActor)
        ren1.AddActor(isoActor)
        ren1.SetBackground(colors.GetColor3d("Black"))
        ren1.GetActiveCamera().SetFocalPoint(0, 0, 0)
        ren1.GetActiveCamera().SetPosition(0, -1, 0)
        ren1.GetActiveCamera().SetViewUp(0, 0, -1)
        ren1.ResetCamera()
        ren1.GetActiveCamera().Dolly(1.5)
        ren1.ResetCameraClippingRange()

        
        iren.Initialize()
