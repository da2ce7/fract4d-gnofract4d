// Fractal.h : Declaration of the CFractal

#ifndef __FRACTAL_H_
#define __FRACTAL_H_

#include "resource.h"       // main symbols
#include <atlctl.h>

class Gf4dFractal {};

#include "fract.h" // main platform-independent calculation class

/////////////////////////////////////////////////////////////////////////////
// CFractal
class ATL_NO_VTABLE CFractal : 
	public CComObjectRootEx<CComSingleThreadModel>,
	public IDispatchImpl<IFractal, &IID_IFractal, &LIBID_FRACTCTLLib>,
	public CComControl<CFractal>,
	public IPersistStreamInitImpl<CFractal>,
	public IOleControlImpl<CFractal>,
	public IOleObjectImpl<CFractal>,
	public IOleInPlaceActiveObjectImpl<CFractal>,
	public IViewObjectExImpl<CFractal>,
	public IOleInPlaceObjectWindowlessImpl<CFractal>,
	public IConnectionPointContainerImpl<CFractal>,
	public IPersistStorageImpl<CFractal>,
	public ISpecifyPropertyPagesImpl<CFractal>,
	public IQuickActivateImpl<CFractal>,
	public IDataObjectImpl<CFractal>,
	public IProvideClassInfo2Impl<&CLSID_Fractal, &DIID__IFractalEvents, &LIBID_FRACTCTLLib>,
	public IPropertyNotifySinkCP<CFractal>,
	public CComCoClass<CFractal, &CLSID_Fractal>,
	public Gf4dFractal
{
	// member variables
	image m_im;
	fractal m_fract;

public:
	CFractal()
	{		
		
	}

DECLARE_REGISTRY_RESOURCEID(IDR_FRACTAL)

DECLARE_PROTECT_FINAL_CONSTRUCT()

BEGIN_COM_MAP(CFractal)
	COM_INTERFACE_ENTRY(IFractal)
	COM_INTERFACE_ENTRY(IDispatch)
	COM_INTERFACE_ENTRY(IViewObjectEx)
	COM_INTERFACE_ENTRY(IViewObject2)
	COM_INTERFACE_ENTRY(IViewObject)
	COM_INTERFACE_ENTRY(IOleInPlaceObjectWindowless)
	COM_INTERFACE_ENTRY(IOleInPlaceObject)
	COM_INTERFACE_ENTRY2(IOleWindow, IOleInPlaceObjectWindowless)
	COM_INTERFACE_ENTRY(IOleInPlaceActiveObject)
	COM_INTERFACE_ENTRY(IOleControl)
	COM_INTERFACE_ENTRY(IOleObject)
	COM_INTERFACE_ENTRY(IPersistStreamInit)
	COM_INTERFACE_ENTRY2(IPersist, IPersistStreamInit)
	COM_INTERFACE_ENTRY(IConnectionPointContainer)
	COM_INTERFACE_ENTRY(ISpecifyPropertyPages)
	COM_INTERFACE_ENTRY(IQuickActivate)
	COM_INTERFACE_ENTRY(IPersistStorage)
	COM_INTERFACE_ENTRY(IDataObject)
	COM_INTERFACE_ENTRY(IProvideClassInfo)
	COM_INTERFACE_ENTRY(IProvideClassInfo2)
END_COM_MAP()

BEGIN_PROP_MAP(CFractal)
	PROP_DATA_ENTRY("_cx", m_sizeExtent.cx, VT_UI4)
	PROP_DATA_ENTRY("_cy", m_sizeExtent.cy, VT_UI4)
	// Example entries
	// PROP_ENTRY("Property Description", dispid, clsid)
	// PROP_PAGE(CLSID_StockColorPage)
END_PROP_MAP()

BEGIN_CONNECTION_POINT_MAP(CFractal)
	CONNECTION_POINT_ENTRY(IID_IPropertyNotifySink)
END_CONNECTION_POINT_MAP()

BEGIN_MSG_MAP(CFractal)
	CHAIN_MSG_MAP(CComControl<CFractal>)
	DEFAULT_REFLECTION_HANDLER()
END_MSG_MAP()
// Handler prototypes:
//  LRESULT MessageHandler(UINT uMsg, WPARAM wParam, LPARAM lParam, BOOL& bHandled);
//  LRESULT CommandHandler(WORD wNotifyCode, WORD wID, HWND hWndCtl, BOOL& bHandled);
//  LRESULT NotifyHandler(int idCtrl, LPNMHDR pnmh, BOOL& bHandled);



// IViewObjectEx
	DECLARE_VIEW_STATUS(VIEWSTATUS_SOLIDBKGND | VIEWSTATUS_OPAQUE)

	// Overrides IOleObjectImpl
	STDMETHOD(SetExtent)( DWORD dwDrawAspect, SIZEL* psizel )
	{
		SIZEL pixSize;
		AtlHiMetricToPixel(psizel,&pixSize);
		
		m_im.set_resolution(pixSize.cx, pixSize.cy);
		
		ATLTRACE(_T("size:(%d, %d)\n"),pixSize.cx, pixSize.cy);

		m_fract.calc(this, &m_im);

		// call original method
		return IOleObjectImpl<CFractal>::SetExtent(dwDrawAspect, psizel);
	}

// IFractal
public:
	HRESULT OnDrawAdvanced(ATL_DRAWINFO& di)
	{
		RECT& rc = *(RECT*)di.prcBounds;
		ATLTRACE(_T("%bounds: (%d %d %d %d)\n"),rc.left, rc.top, rc.right - rc.left, rc.bottom - rc.top);

		int ok = SetDIBitsToDevice(
			di.hdcDraw, 
			rc.left, rc.top, 
			rc.right - rc.left, rc.bottom - rc.top, 
			0 , 0, 
			0 , rc.bottom - rc.top, 
			m_im.buffer, 
			&m_im.m_bmi, 
			DIB_RGB_COLORS);

		return S_OK;
	}
	HRESULT OnDraw(ATL_DRAWINFO& di)
	{
		/*
		RECT& rc = *(RECT*)di.prcBounds;
		//Rectangle(di.hdcDraw, rc.left, rc.top, rc.right, rc.bottom);

		ATLTRACE(_T("%s\n"), m_bInPlaceActive ? _T("active") : _T("inactive"));
		ATLTRACE(_T("%bounds: (%d %d %d %d)\n"),rc.left, rc.top, rc.right - rc.left, rc.bottom - rc.top);

		SetTextAlign(di.hdcDraw, TA_CENTER|TA_BASELINE);
		LPCTSTR pszText = _T("ATL 3.0 : Fractal");
		int ok = SetDIBitsToDevice(
			di.hdcDraw, 
			0, 0, 
			m_im.Xres, m_im.Yres, 
			0 , 0, 
			0 , m_im.Yres, 
			m_im.buffer, 
			&m_im.m_bmi, 
			DIB_RGB_COLORS);

		DWORD dwError = GetLastError();
		*/
		/*
		TextOut(di.hdcDraw, 
			(rc.left + rc.right) / 2, 
			(rc.top + rc.bottom) / 2, 
			pszText, 
			lstrlen(pszText));
		*/
		return S_OK;
	}
};

#endif //__FRACTAL_H_
